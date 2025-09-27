# Message2Book Bot

A Telegram bot that automatically responds to incoming messages with predefined responses.

## Features

- Keyword-based responses
- Business hours logic
- Webhook and polling support
- Rate limiting
- And more!

## Project Structure

```
message2book/
|-- bot/
|   |-- __init__.py
|   |-- main.py         # Main bot application
|   |-- handlers.py     # Message handlers
|   |-- responses.py    # Response logic
|   |-- utils.py        # Utility functions
|   |-- config.py       # Configuration loader
|-- tests/
|   |-- test_handlers.py # Unit tests
|-- .gitignore
|-- config.json.example # Example configuration
|-- requirements.txt
|-- README.md
|-- run.py            # Entry point
|-- webserver.py      # Flask webserver for webhooks
```

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/message2book.git
   cd message2book
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot:**
   - Open `config.json` and configure other settings as needed.
   - **Telegram Bot Token:** Your bot token should be stored in a `.env` file in the project root directory (e.g., `/Users/bpaul/workspace/text2book/message2book/.env`). Add the line `TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN` to this file. To get a Telegram Bot Token, talk to @BotFather on Telegram.

## Running the Bot

### Polling Mode

By default, the bot runs in polling mode. This is useful for development.

```bash
python run.py
```

## Deployment to AWS Lambda with Zappa

Zappa is a tool for deploying Python web applications on AWS Lambda and API Gateway.

1.  **Install Zappa:**
    Zappa is included in `requirements.txt`, so ensure you have installed all dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure AWS Credentials:**
    Ensure you have AWS credentials configured on your system. Zappa uses the AWS CLI configuration (e.g., `~/.aws/credentials` and `~/.aws/config`). You can configure it using `aws configure`.

3.  **Review `zappa_settings.json`:**
    Open `zappa_settings.json` and adjust the settings:
    -   `aws_region`: Set to your desired AWS region (e.g., `us-east-1`).
    -   `profile_name`: If you use a specific AWS CLI profile, set its name here. Otherwise, `default` is used.
    -   `s3_bucket`: **Change this to a globally unique S3 bucket name.** Zappa will create this bucket to store your deployment packages.
    -   `runtime`: Ensure this matches your Python version (e.g., `python3.13`).
    -   `environment_variables`: These are placeholders. You will need to set `TELEGRAM_TOKEN` and `OPENAI_API_KEY` in the AWS Lambda console after deployment, or configure Zappa to read them from your local `.env` during deployment (for production, managing them directly in AWS is recommended).

## Deployment to AWS Lambda with Zappa

Zappa is a tool for deploying Python web applications on AWS Lambda and API Gateway.

1.  **Install Zappa:**
    Zappa is included in `requirements.txt`, so ensure you have installed all dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure AWS Credentials:**
    Ensure you have AWS credentials configured on your system. Zappa uses the AWS CLI configuration (e.g., `~/.aws/credentials` and `~/.aws/config`). You can configure it using `aws configure`.

3.  **Review `zappa_settings.json`:**
    Open `zappa_settings.json` and adjust the settings:
    -   `aws_region`: Set to your desired AWS region (e.g., `us-east-1`).
    -   `profile_name`: If you use a specific AWS CLI profile, set its name here. Otherwise, `default` is used.
    -   `s3_bucket`: **Change this to a globally unique S3 bucket name.** Zappa will create this bucket to store your deployment packages.
    -   `runtime`: Ensure this matches your Python version (e.g., `python3.13`).
    -   `environment_variables`: These are placeholders. You will need to set `TELEGRAM_TOKEN` and `OPENAI_API_KEY` in the AWS Lambda console after deployment, or configure Zappa to read them from your local `.env` during deployment (for production, managing them directly in AWS is recommended).

## DynamoDB Table Setup

The bot uses Amazon DynamoDB to store chat history. You need to create a DynamoDB table with a specific name and primary key.

1.  **Create the DynamoDB Table:**
    You can create the table using the AWS CLI:
    ```bash
    aws dynamodb create-table \
        --table-name TelegramChatHistory \
        --attribute-definitions \
            AttributeName=SessionId,AttributeType=S \
        --key-schema \
            AttributeName=SessionId,KeyType=HASH \
        --provisioned-throughput \
            ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region <YOUR_AWS_REGION>
    ```
    *   Replace `<YOUR_AWS_REGION>` with the AWS region you are deploying to (e.g., `us-east-1`).
    *   `TelegramChatHistory` is the table name used in `langchain_bot/memory.py`.
    *   `SessionId` (String type) is the primary key, which will store the Telegram user ID.

2.  **Grant Lambda Permissions:**
    Your Lambda function (deployed by Zappa) will need permissions to read from and write to this DynamoDB table. You will need to attach an IAM policy to the Lambda function's execution role that grants `dynamodb:GetItem`, `dynamodb:PutItem`, and `dynamodb:DeleteItem` permissions on the `TelegramChatHistory` table. Zappa might create a default role, which you can then modify.

## Amazon OpenSearch Service Setup

The bot uses Amazon OpenSearch Service as a vector database for semantic retrieval of past interactions.

1.  **Create an Amazon OpenSearch Service Domain:**
    *   Go to the AWS OpenSearch Service console.
    *   Create a new domain. Ensure you enable **vector engine** for k-NN search.
    *   Choose appropriate instance types and storage based on your expected usage. For cost-effectiveness, start with a small instance type (e.g., `t3.small.search` or `t2.small.search` if available and sufficient for testing).
    *   Configure network access (VPC access is recommended for security).
    *   Set up fine-grained access control with a master user or IAM roles.

2.  **Configure Access Policies:**
    Your Lambda function's execution role will need permissions to interact with your OpenSearch domain. You will need to attach an IAM policy that grants `es:ESHttpGet`, `es:ESHttpPut`, `es:ESHttpPost`, `es:ESHttpDelete` permissions on your OpenSearch domain.

3.  **Set Environment Variables in Lambda:**
    After deploying your Lambda function with Zappa, you need to set the following environment variables in the AWS Lambda console:
    *   `OPENSEARCH_URL`: The endpoint URL of your OpenSearch domain (e.g., `https://search-your-domain-xxxx.us-east-1.es.amazonaws.com`).
    *   `AWS_ACCESS_KEY_ID`: An AWS access key with permissions to access OpenSearch.
    *   `AWS_SECRET_ACCESS_KEY`: The corresponding secret access key.
    *   `AWS_REGION`: The AWS region where your OpenSearch domain is deployed.

    **Security Note:** For production, it's highly recommended to use IAM roles for authentication instead of directly embedding `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as environment variables. You would then configure your OpenSearch domain's access policy to trust the Lambda function's execution role.

4.  **Deploy the application:**


    ```bash
    zappa deploy dev
    ```
    This command will:
    -   Create an AWS Lambda function.
    -   Create an API Gateway endpoint.
    -   Upload your code.
    -   Output the API Gateway URL.

5.  **Set Telegram Webhook:**
    Once deployed, Zappa will provide an API Gateway URL. You need to set this URL as your Telegram bot's webhook. You can do this by sending a request to the Telegram Bot API:
    ```
    https://api.telegram.org/bot<YOUR_TELEGRAM_TOKEN>/setWebhook?url=<YOUR_API_GATEWAY_URL>/webhook
    ```
    Replace `<YOUR_TELEGRAM_TOKEN>` with your bot's token and `<YOUR_API_GATEWAY_URL>` with the URL provided by Zappa.

6.  **Update `config.json` for Webhook Mode (Optional):**
    If you want your local `config.json` to reflect the deployed webhook, you can update it:
    -   Set `use_webhook` to `true`.
    -   Set `webhook_url` to your API Gateway URL (e.g., `https://<your-api-id>.execute-api.<region>.amazonaws.com/dev/webhook`).

7.  **Update the Lambda Environment Variables:**
    Go to the AWS Lambda console, find your deployed function, and set the `TELEGRAM_TOKEN` and `OPENAI_API_KEY` environment variables directly in the Lambda function's configuration.

## Running Tests

To run the tests, use `pytest`:

```bash
pytest
```