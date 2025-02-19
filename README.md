# Ollama Bot

Ollama Bot is a dynamic Discord bot powered by OpenAI's language models, designed to make your server more interactive and engaging. Chat with the bot, get real-time responses, and enjoy seamless conversations.

## Features

- **Interactive Chat**: Engage with the bot using OpenAI's advanced language models.
- **Real-time Streaming**: Experience smooth, real-time responses.
- **Efficient Updates**: Debounced message updates to keep the chat clean and responsive.
- **Easy Setup**: Quick configuration with your OpenAI API key and model.

## Quick Start

### Prerequisites

- Python 3.8+
- Discord account and server
- OpenAI API key

### Installation

1. **Clone the repo**:

    ```sh
    git clone https://github.com/yourusername/ollama-bot.git
    cd ollama-bot
    ```

2. **Set up a virtual environment**:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

4. **Configure environment variables**:

    Create a `.env` file with:

    ```env
    DISCORD_TOKEN=your_discord_bot_token
    OPENAI_API_KEY=your_openai_api_key
    OPENAI_MODEL=your_openai_model
    ```

### Run the Bot

1. **Start the bot**:

    ```sh
    python main.py
    ```

2. **Invite the bot to your server**:

    Use the [Discord Developer Portal](https://discord.com/developers/applications) to invite your bot.

3. **Chat with the bot**:

    Type `!chat <your message>` in your server to start a conversation.

## Usage

- **!chat <message>**: Chat with the bot and get intelligent responses.

## Contributing

We welcome contributions! Feel free to fork the repo, create a branch, and submit a pull request.

## License

Licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Discord.py](https://github.com/Rapptz/discord.py)
- [OpenAI](https://openai.com/)
- [LangChain](https://github.com/hwchase17/langchain)

---

Enhance your Discord experience with Ollama Bot!
