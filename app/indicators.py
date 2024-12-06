import pandas as pd
from tapy import Indicators


class AddIndicators:
    def __init__(self, df):
        self.df = df
        self.pre_defined_inds()
        self.implement_new_inds()
    
    def pre_defined_inds(self):
        i = Indicators(self.df)
        i.alligator(period_jaws=13, period_teeth=8, period_lips=5, shift_jaws=8, shift_teeth=5, shift_lips=3,
                    column_name_jaws='alligator_jaw', 
                    column_name_teeth='alligator_teeth',
                    column_name_lips='alligator_lips')
        i.awesome_oscillator(column_name='ao')
        i.fractals(column_name_high='fractals_high', column_name_low='fractals_low')
        self.df = i.df
        
    def implement_new_inds(self):
        data_high = self.df.loc[self.df['fractals_high']]
        data_low = self.df.loc[self.df['fractals_low']]
        self.df.loc[list(data_high.index), 'aim_box_high'] = self.df.loc[list(data_high.index), 'High']
        self.df = self.df.ffill(axis=0)
        self.df.loc[list(data_low.index), 'aim_box_low'] = self.df.loc[list(data_low.index), 'Low']
        self.df = self.df.ffill(axis=0)
        self.df['ao_diff'] = self.df['ao'].diff()
