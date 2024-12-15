import logging
import sys
import time
import pandas as pd
from datetime import datetime

import schedule
from indicators import AddIndicators, AlligatorIndicators
from read_data import DataReadYfinance
from signal_strategy import strategy_confirm
from telegram_bot import TelegramBot
from visualize import AlligatorVisualization


def visualize_signal(data_frame, time_frame: int, file_name: str) -> None:
    visualization = AlligatorVisualization(data_frame, time_frame)
    visualization.save_fig(file_name)


def send_notif(
    file_name: str, situation: str, time_frame: int, currency_name: str
) -> None:
    telegram_bot = TelegramBot(
        f"{situation} + in {time_frame} TimeFrame and in {currency_name} currency",
        file_name,
    )
    telegram_bot.send_message()


def process_market(
    reading_data: DataReadYfinance,
    indicator_class: AddIndicators,
) -> tuple[list[bool, str], pd.DataFrame]:
    reading_data.get_data()
    reading_data.data_cleaning()
    df = reading_data.data
    df_with_alligator = indicator_class(df).calculate()
    signal = strategy_confirm(df_with_alligator)
    return signal, df_with_alligator


def main() -> None:
    read_data_obj = DataReadYfinance()
    signal, df_processed = process_market(
        reading_data=read_data_obj,
        indicator_class=AlligatorIndicators,
    )
    is_active, situation = signal

    if is_active:
        file_name = "test"
        visualize_signal(
            data_frame=df,
            time_frame=read_data_obj.time_frame,
            file_name=file_name,
        )
        send_notif(
            file_name=file_name,
            situation=situation,
            time_frame=read_data_obj.time_frame,
            currency_name=read_data_obj.currency_name,
        )


def job():
    try:
        print(datetime.now())
        if datetime.now().minute % 5 == 0:
            print(f"Started Reading Data at {time.strftime('%X')}")
            main()
            print(f"Finished Reading Data at {time.strftime('%X')}")
    except:
        print("Error Running 'task' function")


schedule.every(1).minutes.at(":00").do(job)
while True:
    schedule.run_pending()
    time.sleep(0.1)
