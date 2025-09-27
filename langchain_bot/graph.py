from typing import TypedDict, Annotated, List
import operator
import os
import logging

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from langchain_bot.memory import DynamoDBChatMessageHistory
from langchain_bot.vector_store import get_vector_store, add_messages_to_vector_store, retrieve_relevant_messages

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Get OpenSearch connection details from environment variables
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

# Get DynamoDB table name from environment variables
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")

# Initialize the vector store globally (or on first use)
vector_store = None
if OPENSEARCH_URL:
    try:
        vector_store = get_vector_store(
            opensearch_url=OPENSEARCH_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_region=AWS_REGION,
        )
        logger.info("OpenSearch vector store initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenSearch vector store: {e}")
        vector_store = None
else:
    logger.warning("OPENSEARCH_URL not set. OpenSearch vector store will be disabled.")


# Define the LangGraph State
class AgentState(TypedDict):
    chat_history: Annotated[List[BaseMessage], add_messages]
    user_message: str
    session_id: str # To identify the user's conversation
    relevant_context: str # New field for semantic context

# Node to retrieve chat history from DynamoDB
def retrieve_memory(state: AgentState):
    if not DYNAMODB_TABLE_NAME:
        logger.warning("DYNAMODB_TABLE_NAME not set. DynamoDB memory will be disabled.")
        return {"chat_history": []}
    
    session_id = state["session_id"]
    try:
        history_manager = DynamoDBChatMessageHistory(table_name=DYNAMODB_TABLE_NAME, session_id=session_id)
        logger.info(f"Retrieved chat history for session {session_id} from DynamoDB.")
        return {"chat_history": history_manager.messages}
    except Exception as e:
        logger.error(f"Failed to retrieve chat history from DynamoDB for session {session_id}: {e}")
        return {"chat_history": []}


# Node to retrieve semantic context from OpenSearch
def retrieve_semantic_context(state: AgentState):
    if not vector_store:
        logger.warning("OpenSearch vector store is disabled. No semantic context retrieved.")
        return {"relevant_context": ""}

    user_message = state["user_message"]
    session_id = state["session_id"]

    try:
        relevant_docs = retrieve_relevant_messages(
            vector_store=vector_store,
            query=user_message,
            k=3,
            filter={"session_id": session_id}
        )
        context = "\n".join([doc.page_content for doc in relevant_docs])
        logger.info(f"Retrieved semantic context for session {session_id}.")
        return {"relevant_context": context}
    except Exception as e:
        logger.error(f"Failed to retrieve semantic context from OpenSearch for session {session_id}: {e}")
        return {"relevant_context": ""}


# Node to generate response with LLM
def llm_node(state: AgentState):
    messages = state["chat_history"] + [HumanMessage(content=state["user_message"])]
    relevant_context = state["relevant_context"]

    system_prompt = "You are a helpful AI assistant. Respond to the user's query."
    if relevant_context:
        system_prompt += f"\n\nRelevant past interactions:\n{relevant_context}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"input": state["user_message"], "chat_history": messages})
    logger.info(f"Generated LLM response for session {state['session_id']}.")
    return {"chat_history": [AIMessage(content=response)]} # Add AI response to history

# Node to update chat history in DynamoDB
def update_memory(state: AgentState):
    if not DYNAMODB_TABLE_NAME:
        logger.warning("DYNAMODB_TABLE_NAME not set. DynamoDB memory update skipped.")
        return {}

    session_id = state["session_id"]
    history_manager = DynamoDBChatMessageHistory(table_name=DYNAMODB_TABLE_NAME, session_id=session_id)

    new_human_message = HumanMessage(content=state["user_message"])
    new_ai_message = state["chat_history"][-1]

    try:
        history_manager.add_message(new_human_message)
        history_manager.add_message(new_ai_message)
        logger.info(f"Updated chat history in DynamoDB for session {session_id}.")
    except Exception as e:
        logger.error(f"Failed to update chat history in DynamoDB for session {session_id}: {e}")

    return {} # No state change needed for this node

# Node to update vector store with new messages
def vector_store_update(state: AgentState):
    if not vector_store:
        logger.warning("OpenSearch vector store is disabled. Vector store update skipped.")
        return {}

    session_id = state["session_id"]
    user_message = state["user_message"]
    ai_response = state["chat_history"][-1].content

    try:
        add_messages_to_vector_store(
            vector_store=vector_store,
            messages=[user_message, ai_response],
            metadata={"session_id": session_id}
        )
        logger.info(f"Updated vector store for session {session_id}.")
    except Exception as e:
        logger.error(f"Failed to update vector store for session {session_id}: {e}")

    return {}

# Define the LangGraph workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("retrieve_memory", retrieve_memory)
workflow.add_node("retrieve_semantic_context", retrieve_semantic_context)
workflow.add_node("llm_node", llm_node)
workflow.add_node("update_memory", update_memory)
workflow.add_node("vector_store_update", vector_store_update)

# Define edges
workflow.set_entry_point("retrieve_memory")
workflow.add_edge("retrieve_memory", "retrieve_semantic_context")
workflow.add_edge("retrieve_semantic_context", "llm_node")
workflow.add_edge("llm_node", "update_memory")
workflow.add_edge("update_memory", "vector_store_update")
workflow.set_finish_point("vector_store_update")

# Compile the graph
app = workflow.compile()

def invoke_graph(user_message: str, session_id: str) -> str:
    """Invokes the LangGraph workflow with the user's message and session ID."""
    # Initial state for the graph
    initial_state = {"user_message": user_message, "session_id": session_id, "chat_history": [], "relevant_context": ""}
    result = app.invoke(initial_state)
    # The last message in the chat_history should be the AI's response
    return result["chat_history"][-1].content
