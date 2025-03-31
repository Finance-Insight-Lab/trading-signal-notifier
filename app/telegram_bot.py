import os

import telepot
from dotenv import load_dotenv


class TelegramBot:
    def __init__(self, message, photo_name):
        self.message = message
        self.photo = open(f"{photo_name}.jpg", "rb")
        load_dotenv()
        self.bot = telepot.Bot(os.environ["BOT_TOKEN"])

    def send_message(self):
        self.bot.sendMessage(os.environ["CHANNEL_ID"], self.message)
        self.bot.sendPhoto(os.environ["CHANNEL_ID"], photo=self.photo)
