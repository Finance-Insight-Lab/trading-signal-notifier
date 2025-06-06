import pandas as pd
import yfinance as yf
from typing import Protocol, Tuple


class DataRead(Protocol):
    def __init__(self, currency_name: str, time_frame: str):
        self.data: pd.DataFrame
        self.currency_name: str
        self.time_frame: str

    def get_data(self, length=150):
        ...

    def data_cleaning(self):
        ...


class DataReadYfinance:
    def __init__(self, currency_name: str = "EURUSD", time_frame: str = "5m"):
        self.data: pd.DataFrame
        self.currency_name = currency_name
        self.time_frame = time_frame
        self.interval_to_days_map = {
            "1m": "1d",
            "2m": "1d",
            "5m": "2d",
            "15m": "7d",
            "30m": "14d",
            "60m": "30d",
            "4h": "100d",
            "1d": "150d",
        }

    def get_data(self, length=150) -> None:
        ticker = yf.Ticker(f"{self.currency_name}=X")
        data = ticker.history(
            interval=self.time_frame,
            period=self.interval_to_days_map.get(self.time_frame),
        )
        data = data.tail(length)
        data["date"] = data.index
        data = data.reset_index(drop=True)
        self.data = data[["date", "Open", "High", "Low", "Close"]]

    def data_cleaning(self) -> None:
        new_dates = []
        new_format = "%m-%d-%Y, %H:%M:%S"
        x_dates = self.data["date"]
        for l_date in x_dates:
            new_date_ = l_date.strftime(new_format)
            new_dates.append(new_date_)
        self.data["time_str"] = new_dates
        # self.data = self.data.rename({'bidopen': 'Open', 'bidhigh': 'High', 'bidlow': 'Low', 'bidclose': 'Close'},
        # axis=1)
        self.data = self.data[["Open", "High", "Low", "Close", "time_str"]]
