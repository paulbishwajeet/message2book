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

### Webhook Mode

For production, it is recommended to use webhooks.

1. **Enable Webhook in `config.json`**:
   - Set `use_webhook` to `true`.
   - Set `webhook_url` to your public URL where the bot will be hosted (e.g., `https://your-domain.com/webhook`).

2. **Run the bot**:
   ```bash
   python run.py
   ```

3. **Local Testing with ngrok**:
   If you want to test webhooks locally, you can use `ngrok` to expose your local server to the internet.
   - Install `ngrok`.
   - Run `ngrok http 8080`.
   - Copy the `https` forwarding URL from the ngrok output and set it as your `webhook_url` in `config.json` (e.g., `https://<random-string>.ngrok.io/webhook`).

## Running Tests

To run the tests, use `pytest`:

```bash
pytest
```