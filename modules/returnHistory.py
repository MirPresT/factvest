import sys
from decimal import Decimal as decimal
from .base import IexApi
import pandas as pd, datetime as dt
from .pretty_json import prettyJson as pj

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

IEX = IexApi()

class ReturnHistory:
    def __init__(self, symbols, output_path, range='1y'):
        self.symbols = symbols
        self.range = range
        self.output_path = output_path
        self.execute()
    def rnd(self, n, dec):
        decimals = ''.join(['0' for n in range(0, dec ,1)])
        full_str_dec = '0.{}'.format(decimals)
        return decimal(n).quantize(decimal(full_str_dec))
    def execute(self):
        self.save_data(self.request_data())
    def request_data(self):
        request = {
            'base_endpoint': 'stock',
            'symbols': self.symbols,
            'endpoints': ['chart'],
            'other_options': {'chartInterval': 1, 'range': self.range},
        }
        return IEX.get_data(request)
    def save_data(self, response_data):
        relevant_data = []
        for security_obj in response_data:
            price_history = list(reversed(security_obj['info']['chart']))
            returns = [round(day['changePercent']/100, 4) for day in price_history]
            dates = [day['date'] for day in price_history]
            relevant_data.append((security_obj['symbol'], {'returns': returns, 'dates': dates} ))

        dataframe = self.build_df(relevant_data)
        self.save_to_excel(self.output_path, dataframe)
    def build_df(self, all_return_data):

        columns = [symb for (symb, obj) in all_return_data]
        dates = [obj['dates'] for (symb, obj) in all_return_data]
        returns = [obj['returns'] for (symb, obj) in all_return_data]

        date_lengths = [len(dates) for dates in dates]
        stck_w_lngst_hst = columns[date_lengths.index(max(date_lengths))]
        lngst_hst_len = date_lengths[columns.index(stck_w_lngst_hst)]
        # set the longest record of dates as the dates for the dataframe
        dates_for_df = dates[columns.index(stck_w_lngst_hst)]

        short_hist_stocks = [columns[i] for i, p_list in enumerate(returns) if len(p_list) < lngst_hst_len]
        ok_stocks = [symb for symb in columns if symb not in short_hist_stocks]
        short_hist_lists = [(columns.index(symb), returns[columns.index(symb)]) for symb in short_hist_stocks]
        ok_hist_lists = [(columns.index(symb), returns[columns.index(symb)]) for symb in ok_stocks]

        # Make sure all price lists have the same number of items in their arrays
        # Some arrays may be short due to IPO's during the requested time period
        # The difference in length of the arrays are the missing number of days
        # The difference should be the amount of days to add dummy data or blank price data for

        for tpl in short_hist_lists:
            returns[tpl[0]] = tpl[1] + [None for x in range(0, lngst_hst_len - len(tpl[1]))]

        rows = []
        for x, price in enumerate(returns[0]):
            row = {}
            for i, stock in enumerate(columns):
                row[stock] = returns[i][x]
            rows.append(row)

        return pd.DataFrame(data=rows, index=dates_for_df, columns=columns)
    def save_to_excel(self, file_loc, df):
        columns = list(df.columns.values)
        file_name = '{}\\factvest_return_data.xlsx'.format(file_loc)
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
        info = {
            'sheet_name': 'historical_data',
            'index_label': 'date'
        }
        df.to_excel(writer, **info)
        new_writer = self.format_csv(writer, columns, 12.5, **info)
        new_writer.save()
        print('\n\t -> Finished getting historical return data for your stocks!')
    def format_csv(self, writer, columns, col_width, sheet_name, index_label):
        column_numbers = list(range(0,101))
        first_col = 0
        last_col = column_numbers[len(columns)]
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        header_format = workbook.add_format({
            'align': 'right',
            'indent': 1,
            'valign': 'vcenter',
            'bg_color': '#1f497d',
            'border': 0,
            'font_color': 'white',
            'font_size': 10,
        })
        data_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'indent': 1,
            'num_format': '0.00%',
        })
        worksheet.set_row(0, 22.5)
        worksheet.set_column(first_col, last_col, col_width, data_format)

        column_headers = [index_label] + columns[:]

        for c in column_headers:
            worksheet.write(0, column_headers.index(c), c, header_format)

        return writer

# PriceHistory(['intc', 'aapl', 'spot', 'adbe'], "D:\\OneDrive\\SDSU\\Undergraduate Equity Fund\\Historical Stock Data")