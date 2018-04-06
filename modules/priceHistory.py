import sys
from decimal import Decimal as decimal
from .base import IexApi
import pandas as pd, datetime as dt
from .pretty_json import prettyJson as pj

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

IEX = IexApi()

class PriceHistory:
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
        for security_obj in response_data:
            security_dataframe = self.build_df(security_obj['info']['chart'])
            self.save_to_excel(security_obj['symbol'], self.output_path, security_dataframe)
    def build_df(self, chart_data):

        columns = ['close', 'return', 'norm_return']
        dates = []
        dataframe_data = []

        for period in chart_data:
            date_object = dt.datetime.strptime(period['date'], "%Y-%m-%d").date()
            df_row = {
                "close": period['close'],
                "return": self.rnd(period['changePercent'] / 100, 4),
                "norm_return": self.rnd(period['changeOverTime'], 4),
            }

            dates.append(date_object)
            dataframe_data.append(df_row)

        # dataframe_data.reverse() # i need it from oldest to newest instead of newest to oldest? why?
        # dates.reverse() # same as comment above

        df = pd.DataFrame(data=dataframe_data, index=dates, columns=columns)
        # df['return'] = df.pct_change(1)['close'].round(4) # syntax might be useful later
        # df.drop(df.index[0], inplace=True) # might be useful later
        return df
        # return df.iloc[::-1]
    def save_to_excel(self, symbol, file_loc, df):
        columns = list(df.columns.values)
        file_name = '{}\\{}_data.xlsx'.format(file_loc, symbol)
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
        info = {
            'sheet_name': 'historical_data',
            'index_label': 'date'
        }
        df.to_excel(writer, **info)
        new_writer = self.format_csv(writer, columns, 12.5, **info)
        new_writer.save()
        print('\tDone saving data for | {}'.format(symbol.upper()))
    def format_csv(self, writer, columns, col_width, sheet_name, index_label):
        column_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        last_col = column_letters[len(columns)]
        used_column_letters = "A:" + last_col
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
        return_format = workbook.add_format({
            'num_format': '0.00%',
            'align': 'right',
            'valign': 'vcenter',
            'indent': 1,
        })
        data_format = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'indent': 1,
            'num_format': '0.00',
        })
        worksheet.set_row(0, 22.5)
        worksheet.set_column(used_column_letters, col_width, data_format)
        worksheet.set_column('C:D', None, return_format)

        column_headers = [index_label] + columns[:]

        for c in column_headers:
            worksheet.write(0, column_headers.index(c), c, header_format)

        # custom_fun(workbook, writer, worksheet)

        return writer
