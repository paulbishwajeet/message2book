import json
import os
from typing import List, Dict, Any

import boto3
from botocore.exceptions import ClientError

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, messages_to_dict, messages_from_dict

class DynamoDBChatMessageHistory(BaseChatMessageHistory):
    """Chat message history stored in a DynamoDB table."""

    def __init__(
        self,
        table_name: str,
        session_id: str,
        region_name: str = None,
        boto3_session: boto3.Session = None,
    ):
        self.table_name = table_name
        self.session_id = session_id
        self.region_name = region_name
        self.boto3_session = boto3_session

        if self.boto3_session:
            self.dynamodb = self.boto3_session.resource("dynamodb")
        else:
            self.dynamodb = boto3.resource("dynamodb", region_name=self.region_name)

        self.table = self.dynamodb.Table(self.table_name)

        # Ensure table exists (optional, can be done via CloudFormation/Terraform)
        try:
            self.table.load()
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"DynamoDB table {self.table_name} not found. Please create it.")
                raise
            else:
                raise

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve the messages from DynamoDB."""
        try:
            response = self.table.get_item(Key={"SessionId": self.session_id})
            item = response.get("Item", {})
            if "History" in item:
                # Deserialize messages from JSON string
                raw_messages = json.loads(item["History"])
                messages = messages_from_dict(raw_messages)
                return messages
            return []
        except ClientError as e:
            print(f"Error retrieving messages from DynamoDB: {e}")
            return []

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the chat history in DynamoDB."""
        messages = self.messages
        messages.append(message)
        # Serialize messages to JSON string
        raw_messages = messages_to_dict(messages)
        history_json = json.dumps(raw_messages)

        try:
            self.table.put_item(
                Item={
                    "SessionId": self.session_id,
                    "History": history_json,
                    "UpdatedAt": int(os.times().elapsed), # Simple timestamp
                }
            )
        except ClientError as e:
            print(f"Error adding message to DynamoDB: {e}")

    def clear(self) -> None:
        """Clear session history from DynamoDB."""
        try:
            self.table.delete_item(Key={"SessionId": self.session_id})
        except ClientError as e:
            print(f"Error clearing messages from DynamoDB: {e}")
