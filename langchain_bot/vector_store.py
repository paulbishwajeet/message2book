import os
from typing import List, Dict, Any

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.documents import Document

# Initialize OpenAI Embeddings
# Ensure OPENAI_API_KEY is set in your environment variables
embeddings = OpenAIEmbeddings()

def get_opensearch_client(
    host: str,
    port: int = 443,
    use_ssl: bool = True,
    verify_certs: bool = True,
    connection_class: Any = RequestsHttpConnection,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    aws_region: str = None,
) -> OpenSearch:
    """
    Returns an OpenSearch client instance, configured for AWS authentication if credentials are provided.
    """
    if aws_access_key_id and aws_secret_access_key and aws_region:
        awsauth = AWS4Auth(
            aws_access_key_id,
            aws_secret_access_key,
            aws_region,
            'es' # service name for OpenSearch
        )
        return OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=awsauth,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            connection_class=connection_class,
            pool_maxsize=20,
        )
    else:
        # For local OpenSearch or if AWS auth is not needed
        return OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=('user', 'password'), # Replace with actual credentials for local
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            connection_class=connection_class,
            pool_maxsize=20,
        )

def get_vector_store(
    opensearch_url: str,
    index_name: str = "telegram-chat-embeddings",
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    aws_region: str = None,
) -> OpenSearchVectorSearch:
    """
    Initializes and returns an OpenSearchVectorSearch instance.
    """
    # Extract host from URL
    host = opensearch_url.replace("https://", "").split(":")[0]

    client = get_opensearch_client(
        host=host,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_region=aws_region,
    )

    # Ensure the index exists with the correct mapping for vector search
    # This is a basic example, you might need a more robust index creation
    if not client.indices.exists(index=index_name):
        client.indices.create(
            index=index_name,
            body={
                "settings": {
                    "index.knn": True,
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": 1536 # Dimension for OpenAIEmbeddings
                        },
                        "text": {
                            "type": "text"
                        },
                        "metadata": {
                            "type": "object"
                        }
                    }
                }
            }
        )

    vector_store = OpenSearchVectorSearch(
        index_name=index_name,
        embedding_function=embeddings,
        opensearch_url=opensearch_url,
        http_auth=(aws_access_key_id, aws_secret_access_key) if aws_access_key_id else None, # For basic auth if not AWS auth
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        client=client # Pass the configured client
    )
    return vector_store

def add_messages_to_vector_store(
    vector_store: OpenSearchVectorSearch,
    messages: List[str],
    metadata: Dict[str, Any] = None,
):
    """Adds a list of messages to the vector store."""
    documents = [Document(page_content=msg, metadata=metadata) for msg in messages]
    vector_store.add_documents(documents)

def retrieve_relevant_messages(
    vector_store: OpenSearchVectorSearch,
    query: str,
    k: int = 3,
    filter: Dict[str, Any] = None,
) -> List[Document]:
    """Retrieves semantically relevant messages from the vector store."""
    return vector_store.similarity_search(query, k=k, filter=filter)
