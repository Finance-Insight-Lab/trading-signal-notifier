import pandas as pd
import numpy as np
import datetime as dt
import plotly.graph_objects as go
from visualize import AlligatorVisualization
from telegram_bot import TelegramBot
from indicators import AddIndicators
from read_data import DataReadYfinance
from signal_strategy import strategy_confirm
import plotly
import schedule
import time
from datetime import datetime
import sys
import logging

sys.stdout.write('AlligBot started!\n')
logging.info('This is a log message')


def task(reading_data):
    reading_data.get_data()
    reading_data.data_cleaning()
    df = reading_data.data
    ind_add = AddIndicators(df)
    ind_add.df
    df = ind_add.df
    df = df.iloc[50:]
    df = df.reset_index(drop=True)
    status = strategy_confirm(df)
    print('status: ', status)

    if status[0]:
        message_text = status[1]
        vis = AlligatorVisualization(df, 5)
        vis.save_fig('test')
        telegram_bot = TelegramBot(message_text + f' in 5m TimeFrame', 'test')
        telegram_bot.send_message()


reading_data = DataReadYfinance()

print(f"started at {time.strftime('%X')}")
print(f"connection to Yfinance started at {time.strftime('%X')}")


def job():
    try:
        print(datetime.now())
        if datetime.now().minute % 5 == 0:
            print(f"Started Reading Data at {time.strftime('%X')}")
            task(reading_data)
            print(f"Finished Reading Data at {time.strftime('%X')}")
    except:
        print("Error Running 'task' function")


schedule.every(1).minutes.at(':00').do(job)
while True:
    schedule.run_pending()
    time.sleep(0.1)
