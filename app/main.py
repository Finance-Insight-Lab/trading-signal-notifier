import ast
import os
import time
import traceback
from datetime import datetime
from typing import Tuple, List, Callable
from dataclasses import dataclass

import pandas as pd
import schedule
from dotenv import load_dotenv
from indicators import AddAlligatorIndicators, AddIndicators
from read_data import DataRead, DataReadYfinance
from signal_strategy import AlligatorStrategyConfirm, StrategyConfirm
from telegram_bot import TelegramBot
from visualize import AlligatorVisualization, StrategyVisualization

@dataclass
class Config:
    currencies: List[str]
    time_frames: List[str]
    time_offset: int

load_dotenv()
config = Config(
    currencies=ast.literal_eval(os.environ.get("CURRENCIES_LIST", "[]")),
    time_frames=ast.literal_eval(os.environ.get("TIME_FRAMES", "[]")),
    time_offset=int(os.environ.get("TIME_OFFSET", 0)),
)

def read_market_data(reader: DataRead) -> pd.DataFrame:
    reader.get_data()
    reader.data_cleaning()
    return reader.data


def process_market(
    market_data: pd.DataFrame,
    indicator: AddIndicators,
    strategy: StrategyConfirm,
) -> Tuple[Tuple[bool, str], pd.DataFrame]:
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
    currency_name: str,
    time_frame: str,
    data_reader: DataRead,
    indicator: AddIndicators,
    strategy: StrategyConfirm,
    visualizer: StrategyVisualization,
    notifier: Callable[[str, str, str, str], None],
) -> None:
    data_reader.currency_name = currency_name
    data_reader.time_frame = time_frame
    market_data = read_market_data(reader=data_reader)

    indicator.df = market_data

    signal, df_processed = process_market(
        market_data=market_data,
        indicator=indicator,
        strategy=strategy,
    )
    is_active, situation = signal

    if is_active:
        file_name = "test"
        visualizer.data = df_processed
        visualizer.time_frame = time_frame
        visualizer.file_name = file_name
        visualize_signal(visualizer)
        notifier(file_name, situation, time_frame, currency_name)


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
            if now.minute == 0 and (now.hour - config.time_offset) % time == 0:
                valid_tfs.append(tf)
        elif frame == "d":
            if now.minute == 0 and now.hour == 0 and now.day % time == 0:
                valid_tfs.append(tf)
        else:
            continue

    return valid_tfs


def run_strategy_job():
    try:
        tfs = check_time_frames(time_frames=config.time_frames)
        print(datetime.now())
        for time_frame in tfs:
            print(f"Started Reading Data at {time.strftime('%X')}")
            for currency_name in config.currencies:
                reader = DataReadYfinance()
                indicator = AddAlligatorIndicators()
                strategy = AlligatorStrategyConfirm()
                visualizer = AlligatorVisualization()
                main(
                    currency_name=currency_name,
                    time_frame=time_frame,
                    data_reader=reader,
                    indicator=indicator,
                    strategy=strategy,
                    visualizer=visualizer,
                    notifier=send_notif,
                )
            print(f"Finished Reading Data at {time.strftime('%X')}")
    except:
        traceback_str = traceback.format_exc()
        print("Error Running 'task' function")
        print(f"error: {traceback_str}")


schedule.every(1).minutes.at(":00").do(run_strategy_job)
while True:
    schedule.run_pending()
    time.sleep(0.1)
