import ast
import os
import time
from datetime import datetime
from typing import Tuple

import pandas as pd
import schedule
from dotenv import load_dotenv
from indicators import AddAlligatorIndicators, AddIndicators
from read_data import DataRead, DataReadYfinance
from signal_strategy import AlligatorStrategyConfirm, StrategyConfirm
from telegram_bot import TelegramBot
from visualize import AlligatorVisualization, StrategyVisualization

load_dotenv()
currencis_list: list = ast.literal_eval(os.environ.get("CURRENCIES_LIST", "[]"))
time_frames: list = ast.literal_eval(os.environ.get("TIME_FRAMES", "[]"))


def read_market_data(reader: DataRead) -> pd.DataFrame:
    reader.get_data()
    reader.data_cleaning()
    return reader.data


def process_market(
    market_data: pd.DataFrame,
    indicator: AddIndicators,
    strategy: StrategyConfirm,
) -> tuple[Tuple[bool, str], pd.DataFrame]:
    df_with_indicator = indicator.calculate_indicators()
    signal = strategy.strategy_confirm(df_with_indicator)
    return signal, df_with_indicator


def visualize_signal(visualization: StrategyVisualization) -> None:
    visualization.create()


def send_notif(
    file_name: str, situation: str, time_frame: str, currency_name: str
) -> None:
    telegram_bot = TelegramBot(
        f"{situation} in {time_frame} timeframe, in {currency_name} currency",
        file_name,
    )
    telegram_bot.send_message()


def main(
    currency_name: str = "EURUSD",
    time_frame: str = "5m",
    data_reader: DataRead = DataReadYfinance(),
    strategy: StrategyConfirm = AlligatorStrategyConfirm(),
) -> None:
    data_reader.currency_name, data_reader.time_frame = currency_name, time_frame
    market_data = read_market_data(reader=data_reader)
    signal, df_processed = process_market(
        market_data=market_data,
        indicator=AddAlligatorIndicators(market_data),
        strategy=strategy,
    )
    is_active, situation = signal

    if is_active:
        file_name = "test"
        visualize_signal(
            visualization=AlligatorVisualization(
                ohlc_data=df_processed, time_frame=time_frame, file_name=file_name
            ),
        )
        send_notif(
            file_name=file_name,
            situation=situation,
            time_frame=time_frame,
            currency_name=currency_name,
        )


def check_time_frames(time_frames: list) -> list:
    valid_tfs = []
    valid_fs = ("m", "h", "d")
    for tf in time_frames:
        time = int(tf[:-1])  # e.g. in `15m`, `time = 15`
        frame = tf[-1]  # e.g. in `15m`, `frame = minute`
        if frame not in valid_fs:
            continue
        now = datetime.utcnow()
        if frame == "m":
            if now.minute % time == 0:
                valid_tfs.append(tf)
        elif frame == "h":
            if now.hour % time == 2 and now.minute == 0:
                valid_tfs.append(tf)
        elif frame == "d":
            if now.day % time == 0 and now.hour == 0 and now.minute == 0:
                valid_tfs.append(tf)
        else:
            continue

    return valid_tfs


def job():
    try:
        tfs = check_time_frames(time_frames=time_frames)
        print(datetime.now())
        for time_frame in tfs:
            print(f"Started Reading Data at {time.strftime('%X')}")
            for currency_name in currencis_list:
                main(
                    currency_name=currency_name,
                    time_frame=time_frame,
                    strategy=AlligatorStrategyConfirm(),
                )
            print(f"Finished Reading Data at {time.strftime('%X')}")
    except:
        print("Error Running 'task' function")


schedule.every(1).minutes.at(":00").do(job)
while True:
    schedule.run_pending()
    time.sleep(0.1)
