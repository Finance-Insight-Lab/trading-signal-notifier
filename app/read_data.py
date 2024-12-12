import yfinance as yf


class DataReadYfinance:
    def __init__(self, currency_name="EURUSD", time_frame=5):
        self.data = None
        self.currency_name = currency_name
        self.time_frame = time_frame

    def get_data(self, currency="EURUSD", period="5m", duration="2d", length=150):
        ticker = yf.Ticker(f"{currency}=X")
        data = ticker.history(interval=period, period="2d")
        data = data.tail(length)
        data['date'] = data.index
        data = data.reset_index(drop=True)
        self.data = data[['date', 'Open', 'High', 'Low', 'Close']]

    def data_cleaning(self):
        new_dates = []
        new_format = "%m-%d-%Y, %H:%M:%S"
        x_dates = self.data['date']
        for l_date in x_dates:
            new_date_ = l_date.strftime(new_format)
            new_dates.append(new_date_)
        self.data['time_str'] = new_dates
        # self.data = self.data.rename({'bidopen': 'Open', 'bidhigh': 'High', 'bidlow': 'Low', 'bidclose': 'Close'},
        # axis=1)
        self.data = self.data[['Open', 'High', 'Low', 'Close', 'time_str']]
