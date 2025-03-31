# Trading Signal Notifier

## TL;DR
Trading Signal Notifier is a Docker-based tool that sends notifications when predefined trading conditions are met. It supports multi-timeframe and multi-asset signaling, with plans for multi-strategy and multi-platform support. Ideal for manual traders seeking timely alerts across various platforms.

## Key Features
* Multi-Timeframe Support: Monitor trading signals across different timeframes.
* Multi-Asset Support: Receive notifications for multiple financial assets.
* Future Development: Plans include support for multiple trading strategies and data sources.

## Prerequisites
* Docker
* Telegram Bot and Channel

## Installation
* Clone the repository: `git clone https://github.com/aligheshlaghi97/trading-signal-notifier.git`
* Navigate to the project directory: `cd trading-signal-notifier`
* Build the Docker image: `docker-compose build`

## Usage
* Start the Docker container: `docker-compose up -d`
* To stop the container: `docker-compose down`

## Configuration
You have to make a telegram bot from [BotFather](https://t.me/BotFather). Then make a channel and make that bot an admin of your channel (with message sending permissions).
The program uses environment variables for configuration. You can set these variables by creating a `.env` file in the project directory `app/.env` with the following values (like `.envsample`):

* `BOT_TOKEN`: Your Bot Telegram API key
* `CHANNEL_ID`: The name of the Telegram channel to send notifications to
* `CURRENCIES_LIST`: List of currencies to check for your setups
* `TIME_FRAMES`: List of time frames to check for your setups

## Telegram Channel
Sample messages and images are sent to [this Telegram channel](https://t.me/alligator_signal).
Please feel free to join the channel to stay updated on the signals.

## Contributing
To contribute code, submit a pull request with:

* Create a new branch for your changes
* Follow the existing code style and conventions
* Write clear commit messages and include any necessary documentation or tests
