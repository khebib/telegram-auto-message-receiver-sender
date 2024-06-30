# Telegram Message Receiver/Sender Bot

This Python application allows you to receive and forward messages between Telegram channels and groups. It's designed to simplify the process of managing Telegram messages programmatically.

## Features

- **Receive Messages**: Fetch messages from specified Telegram channels/groups.
- **Forward Messages**: Automatically forward received messages to another Telegram group.
- **User Interaction**: Uses a graphical interface (GUI) to input API credentials and manage settings.
- **Error Handling**: Provides feedback on errors such as invalid media formats or chat restrictions.

## Requirements

- Python 3.x
- `telethon` library (`pip install telethon`)
- `colorama` library (`pip install colorama`)
- `tkinter` library (usually included in Python installations)

## Setup Instructions

1. Clone the repository:
git clone https://github.com/khebib/telegram-message-bot.git
cd telegram-message-bot


2. Install dependencies:
pip install -r requirements.txt


3. Configure `config.json`:
- Replace placeholders with your Telegram API credentials and other settings.

4. Run the application:
python main.py



## Usage

- **Start Bot**: Click the "Start Bot" button in the GUI to initialize the bot.
- **Stop Bot**: Click the "Stop Bot" button to disconnect the bot from Telegram.

## Contributing

Contributions are welcome! If you find any issues or have suggestions, please submit an issue or a pull request on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
