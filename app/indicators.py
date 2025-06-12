import pandas as pd
from tapy import Indicators
from typing import Protocol


class AddIndicators(Protocol):
    df: pd.DataFrame

    def calculate_indicators(self) -> pd.DataFrame:
        ...


class AddAlligatorIndicators:
    def __init__(self, df: pd.DataFrame = pd.DataFrame()):
        self.df = df

    def _pre_defined_inds(self):
        i = Indicators(self.df)
        i.alligator(
            period_jaws=13,
            period_teeth=8,
            period_lips=5,
            shift_jaws=8,
            shift_teeth=5,
            shift_lips=3,
            column_name_jaws="alligator_jaw",
            column_name_teeth="alligator_teeth",
            column_name_lips="alligator_lips",
        )
        i.awesome_oscillator(column_name="ao")
        i.fractals(column_name_high="fractals_high", column_name_low="fractals_low")
        self.df = i.df

    def _implement_new_inds(self):
        data_high = self.df.loc[self.df["fractals_high"]]
        data_low = self.df.loc[self.df["fractals_low"]]
        self.df.loc[list(data_high.index), "aim_box_high"] = self.df.loc[
            list(data_high.index), "High"
        ]
        self.df = self.df.ffill(axis=0)
        self.df.loc[list(data_low.index), "aim_box_low"] = self.df.loc[
            list(data_low.index), "Low"
        ]
        self.df = self.df.ffill(axis=0)
        self.df["ao_diff"] = self.df["ao"].diff()

    def _prepare_for_signal(self):
        self.df = self.df.iloc[50:]
        self.df = self.df.reset_index(drop=True)

    def calculate_indicators(self):
        self._pre_defined_inds()
        self._implement_new_inds()
        self._prepare_for_signal()
        return self.df
