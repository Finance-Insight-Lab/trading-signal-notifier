from typing import Protocol

import pandas as pd
import plotly
import plotly.graph_objects as go


class StrategyVisualization(Protocol):
    def create(self) -> None: ...


class AlligatorVisualization:
    def __init__(
        self, ohlc_data: pd.DataFrame, time_frame: str = "5m", file_name: str = "test"
    ):
        self.time_frame = time_frame
        self.file_name = file_name
        self.fig = plotly.tools.make_subplots(
            rows=4,
            cols=1,
            specs=[[{"rowspan": 3}], [None], [None], [{}]],
            vertical_spacing=0.01,
        )
        self.data = ohlc_data

    def plot_ohlc(self, tf):
        self.fig.add_trace(
            go.Candlestick(
                x=self.data["time_str"],
                open=self.data["Open"],
                high=self.data["High"],
                low=self.data["Low"],
                name=f"Timeframe {tf}",
                close=self.data["Close"],
            )
        )

    # plot alligator lips, teeth and jaw
    def plot_alligator(self):
        self.fig.add_trace(
            go.Scatter(
                name="alligator_lips",
                x=self.data["time_str"],
                y=self.data["alligator_lips"],
                line=dict(color="green", width=1.6),
            )
        )
        self.fig.add_trace(
            go.Scatter(
                name="alligator_teeth",
                x=self.data["time_str"],
                y=self.data["alligator_teeth"],
                line=dict(color="red", width=1.6),
            )
        )
        self.fig.add_trace(
            go.Scatter(
                name="alligator_jaw",
                x=self.data["time_str"],
                y=self.data["alligator_jaw"],
                line=dict(color="blue", width=1.6),
            )
        )

    def plot_fractals(self):
        fractal_high = self.data.loc[self.data["fractals_high"]]
        self.fig.add_trace(
            go.Scatter(
                mode="markers",
                x=fractal_high["time_str"],
                y=fractal_high["High"],
                marker_symbol="triangle-down",
                marker_line_color="midnightblue",
                marker_color="red",
                marker_size=7,
                name="aims high",
            )
        )

        fractal_low = self.data.loc[self.data["fractals_low"]]
        self.fig.add_trace(
            go.Scatter(
                mode="markers",
                x=fractal_low["time_str"],
                y=fractal_low["Low"],
                marker_symbol="triangle-up",
                marker_line_color="midnightblue",
                marker_color="blue",
                marker_size=7,
                name="aims low",
            )
        )

    @staticmethod
    def set_color(ocs, diff_ocs):
        if ocs > 0:
            if diff_ocs > 0:
                color = "lightgreen"
            else:
                color = "darkgreen"
        else:
            if diff_ocs > 0:
                color = "darkred"
            else:
                color = "red"

        return color

    def plot_ao_indicator(self):
        self.fig.append_trace(
            go.Bar(
                x=self.data["time_str"],
                y=self.data["ao"],
                marker=dict(
                    color=list(
                        map(self.set_color, self.data["ao"], self.data["ao_diff"])
                    )
                ),
                name="AO oscillator",
            ),
            row=4,
            col=1,
        )

    def plot_aims_box(self):
        self.fig.add_trace(
            go.Scatter(
                name="aim box high",
                x=self.data["time_str"],
                y=self.data["aim_box_high"],
                line=dict(color="gray", width=1),
            )
        )
        self.fig.add_trace(
            go.Scatter(
                name="aims box low",
                x=self.data["time_str"],
                y=self.data["aim_box_low"],
                line=dict(color="gray", width=1),
            )
        )

    def fig_style(self):
        self.fig.update_layout(
            autosize=False, width=1000, height=700, xaxis_rangeslider_visible=False
        )
        self.fig.update_xaxes(showticklabels=False)

    def show_fig(self):
        self.fig.show()

    def save_fig(self, fig_name):
        self.fig.write_image(f"{fig_name}.jpg")

    def create(self) -> None:
        self.plot_ohlc(self.time_frame)
        self.plot_alligator()
        self.plot_fractals()
        self.plot_ao_indicator()
        self.plot_aims_box()
        self.fig_style()
        self.save_fig(self.file_name)
