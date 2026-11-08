import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
print(f"__file__: {__file__}")

import main as app
from read_data import DataReadYfinance
from signal_strategy import AlligatorStrategyConfirm


class CannedMarket:
    """Stand-in for the live price feed. Zigzag prices so indicators have swings."""

    def __init__(self):
        self.currency_name = ""
        self.time_frame = ""
        self.data = None

    def get_data(self, length=150):
        n = 120
        dates = pd.date_range("2024-01-02", periods=n, freq="5min")
        close = [100.0 + (i % 10) for i in range(n)]
        self.data = pd.DataFrame(
            {
                "date": dates,
                "Open": close,
                "High": [price + 0.5 for price in close],
                "Low": [price - 0.5 for price in close],
                "Close": close,
            }
        )

    def data_cleaning(self):
        self.data["time_str"] = [
            stamp.strftime("%m-%d-%Y, %H:%M:%S") for stamp in self.data["date"]
        ]
        self.data = self.data[["Open", "High", "Low", "Close", "time_str"]]


def test_quiet_market_does_not_notify(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    seen = {}

    class NoSignal:
        def strategy_confirm(self, df):
            seen["rows"] = len(df)
            seen["columns"] = set(df.columns)
            return False, ""

    app.main(data_reader=CannedMarket(), strategy=NoSignal())

    assert seen["rows"] > 0
    assert {"alligator_lips", "alligator_teeth", "alligator_jaw"} <= seen["columns"]
    assert not (tmp_path / "test.jpg").exists()


def test_active_signal_saves_chart_and_notifies(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sent = {}

    class FakeTelegram:
        def __init__(self, message, photo_name):
            sent["message"] = message
            sent["photo"] = Path(f"{photo_name}.jpg").read_bytes()

        def send_message(self):
            sent["sent"] = True

    class SignalOn:
        def strategy_confirm(self, df):
            return True, "Upside Down"

    monkeypatch.setattr(app, "TelegramBot", FakeTelegram)
    app.main(
        currency_name="EURUSD",
        time_frame="5m",
        data_reader=CannedMarket(),
        strategy=SignalOn(),
    )

    assert sent["sent"] is True
    assert sent["message"] == "Upside Down in 5m timeframe, in EURUSD currency"
    assert sent["photo"]


def _bars(count, **fields):
    return [dict(fields) for _ in range(count)]


def test_upside_cross_is_a_signal():
    bars = _bars(
        5,
        alligator_lips=10,
        alligator_teeth=8,
        alligator_jaw=6,
        Low=11,
        High=12,
        Close=11.5,
    )
    bars.append(
        dict(
            alligator_lips=10,
            alligator_teeth=8,
            alligator_jaw=6,
            Low=9,
            High=12,
            Close=10.5,
        )
    )

    assert AlligatorStrategyConfirm().strategy_confirm(pd.DataFrame(bars)) == (
        True,
        "Upside Down",
    )


def test_downside_cross_is_a_signal():
    bars = _bars(
        5,
        alligator_lips=10,
        alligator_teeth=12,
        alligator_jaw=14,
        Low=8,
        High=9,
        Close=8.5,
    )
    bars.append(
        dict(
            alligator_lips=10,
            alligator_teeth=12,
            alligator_jaw=14,
            Low=8,
            High=11,
            Close=9.5,
        )
    )

    assert AlligatorStrategyConfirm().strategy_confirm(pd.DataFrame(bars)) == (
        True,
        "Downside up",
    )


def test_aligned_market_without_a_cross_stays_quiet():
    bars = _bars(
        6,
        alligator_lips=10,
        alligator_teeth=8,
        alligator_jaw=6,
        Low=11,
        High=12,
        Close=11.5,
    )

    assert AlligatorStrategyConfirm().strategy_confirm(pd.DataFrame(bars)) == (
        False,
        "",
    )


def test_only_due_timeframes_are_kept(monkeypatch):
    current = {}

    class Clock:
        @staticmethod
        def utcnow():
            return current["now"]

    monkeypatch.setattr(app, "datetime", Clock)

    current["now"] = datetime(2024, 1, 2, 2, 15)
    assert app.check_time_frames(["15m", "5m", "30m", "4h", "1d", "5x"]) == [
        "15m",
        "5m",
    ]

    current["now"] = datetime(2024, 1, 2, 2, 0)
    assert app.check_time_frames(["30m", "4h", "1d"]) == ["30m", "4h"]

    current["now"] = datetime(2024, 1, 2, 0, 0)
    assert app.check_time_frames(["1d", "4h"]) == ["1d"]


def test_job_checks_each_currency_on_due_timeframes(monkeypatch):
    calls = []
    monkeypatch.setattr(app, "time_frames", ["15m", "30m"])
    monkeypatch.setattr(app, "currencis_list", ["EURUSD", "GBPUSD"])
    monkeypatch.setattr(app, "check_time_frames", lambda time_frames: ["15m"])
    monkeypatch.setattr(
        app,
        "main",
        lambda **kwargs: calls.append((kwargs["currency_name"], kwargs["time_frame"])),
    )

    app.job()

    assert calls == [("EURUSD", "15m"), ("GBPUSD", "15m")]


def test_cleaned_prices_keep_ohlc_and_a_time_string():
    reader = DataReadYfinance()
    reader.data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02 10:15:00"]),
            "Open": [1.1],
            "High": [1.2],
            "Low": [1.0],
            "Close": [1.15],
            "Volume": [9],
        }
    )

    reader.data_cleaning()

    assert list(reader.data.columns) == ["Open", "High", "Low", "Close", "time_str"]
    assert reader.data.loc[0, "time_str"] == "01-02-2024, 10:15:00"
