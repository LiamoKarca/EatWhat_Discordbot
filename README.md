# EatWhat Discord Bot

This Discord bot helps users find nearby open restaurants and record searched landmarks. It supports multiple users and
offers an easy-to-use command list and landmark search record menu. Designed to be simple and clear, it provides rich
functionality and detailed consideration. Whether you're looking for a good restaurant or recording nearby restaurants
of your landmarks, this bot is your powerful assistant.

## Table of Contents

- [Installation](#installation)
- [Environment Variable](#environment-variable)
- [Starting the Bot](#starting-the-bot)
- [Bot Commands](#bot-commands)
- [Contributing](#contributing)
- [License](#license)
- [Contact Information](#contact-information)

## Installation

1. **Python**: Ensure Python is installed on your system.
2. **pip** (Python package installer): Make sure you have pip installed.

### Required Packages

You can install the required packages using the following command:

```bash
pip install -r requirements.txt
```

## Environment Variable

1. You need to visit [Discord Developers](https://discord.com/developers/applications) and create an application to
   obtain a `Token`.

2. To run the Discord bot and configure the deployment settings, you need to set the following environment variable :

```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
```

## Starting the Bot

cd to your current project path.

```bash
python bot.py
```

### Inviting the Bot to the Server

Remember to invite the bot to the server. The invitation link can be generated
at [Discord Developers](https://discord.com/developers/applications).

## Bot Commands

Once the bot is running and connected to Discord, you can interact with it using various commands. These commands can be
customized according to the bot's functionalities.

- `/eatwhat landmark:` -> Enter the landmark you want to search for nearby restaurants.

- `/ewrandom request_id:` -> Select a landmark you have previously entered from the shortcut menu, and the bot will
  randomly recommend a nearby restaurant.

- `/ewclear request_id:` ->  Clears a specific landmark record that you have previously entered and removes it from the
  shortcut menu. Please note, this command can only clear one landmark record at a time, not all at once.

## Contributing

If you'd like to contribute to this app development, feel free to fork this repository, make your changes, and submit a
pull request. Please ensure your code follows the project's coding standards and includes appropriate documentation for
any new features or changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact Information

If you have any questions or issues related to the project, feel free to open an issue on GitHub.

---
