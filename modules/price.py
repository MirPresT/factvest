import sys
from .base import IexApi
from .money import money, rnd
import pandas as pd, datetime as dt
from .pretty_json import prettyJson as pj

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

IEX = IexApi()

class Price:
    def __init__(self, symbols):
        self.symbols = symbols
    def get_price(self):
        return self.request_data()
    def request_data(self):
        request = {
            'base_endpoint': 'stock',
            'symbols': self.symbols,
            'endpoints': ['price'],
            'other_options': {},
        }
        return IEX.get_data(request)
