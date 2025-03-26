from typing import Protocol, Tuple

import pandas as pd


class StrategyConfirm(Protocol):
    def strategy_confirm(self, df: pd.DataFrame) -> Tuple[bool, str]: ...


class AlligatorStrategyConfirm:
    def strategy_confirm(self, df: pd.DataFrame) -> Tuple[bool, str]:
        if (
            (df.iloc[-6:-1]["alligator_lips"] > df.iloc[-6:-1]["alligator_teeth"]).all()
            and (
                df.iloc[-6:-1]["alligator_teeth"] > df.iloc[-6:-1]["alligator_jaw"]
            ).all()
            and (df.iloc[-6:-1]["Low"] > df.iloc[-6:-1]["alligator_lips"]).all()
        ):
            if (
                (df.iloc[-1]["Low"] < df.iloc[-1]["alligator_lips"])
                and (df.iloc[-2]["Low"] > df.iloc[-2]["alligator_lips"])
                and (df.iloc[-1]["Close"] > df.iloc[-1]["alligator_lips"])
            ):
                return True, "Upside Down"

        elif (
            (df.iloc[-6:-1]["alligator_jaw"] > df.iloc[-6:-1]["alligator_teeth"]).all()
            and (
                df.iloc[-6:-1]["alligator_teeth"] > df.iloc[-6:-1]["alligator_lips"]
            ).all()
            and (df.iloc[-6:-1]["High"] < df.iloc[-6:-1]["alligator_lips"]).all()
        ):
            if (
                (df.iloc[-1]["High"] > df.iloc[-1]["alligator_lips"])
                and (df.iloc[-2]["High"] < df.iloc[-2]["alligator_lips"])
                and (df.iloc[-1]["Close"] < df.iloc[-1]["alligator_lips"])
            ):
                return True, "Downside up"
        return False, ""
