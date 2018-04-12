import sys
from decimal import Decimal as decimal
from .base import IexApi
import pandas as pd, datetime as dt
from .pretty_json import prettyJson as pj

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

IEX = IexApi()

class Performance:
    def __init__(self, symbols, output_path):
        self.symbols = symbols
        self.output_path = output_path
        self.run()
    def run(self):
        self.save_data(self.request_data())
    def request_data(self):
        request = {
            'base_endpoint': 'stock',
            'symbols': self.symbols,
            'endpoints': ['chart'],
            'other_options': {'chartInterval': 1, 'range': '5y'}
        }
        return IEX.get_data(request)
    def save_data(self, response_data):
        df = self.create_df(response_data)
        file_name = 'perf_stats_factvest'
        self.save_to_excel(file_name, self.output_path, df)
    def save_to_excel(self, file_name, output_path, df):
        columns = list(df.columns.values)
        info = {'sheet_name':'performance', 'index_label':'symbol'}
        file_path = '{}\\{}.xlsx'.format(output_path, file_name)
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        df.to_excel(writer, **info)
        new_writer = self.format_csv(
            writer, columns,
            13.57, **info
        )
        new_writer.save()
        print('\tDone saving file | {}'.format(file_name))
    def create_df(self, response_data):
        index_column = []
        dataframe_data = []
        columns = ['5 day chg']

        for company in response_data:
            trade_info = company['info']['chart']
            recent_price = trade_info[len(trade_info) - 1]['close']

            prior_trade_obj = trade_info[len(trade_info) - (5 + 1)]
            prior_price = prior_trade_obj['close']
            prior_date = prior_trade_obj['date']
            perc_change = round(((recent_price / prior_price) - 1), 4)
            index_column.append(company['symbol'])
            dataframe_data.append({'5 day chg': perc_change})
        df = pd.DataFrame(data=dataframe_data, columns=columns, index=index_column)
        return df
    def format_csv(self, writer, columns, col_width, sheet_name, index_label):
        column_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        last_col = column_letters[len(columns)]
        used_column_letters = "A:" + last_col
        non_date_cols = "B:" + last_col
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        col_1_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
        })
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

        worksheet.set_row(0, 22.5)
        worksheet.set_column(0, 0, cell_format=col_1_format)
        worksheet.set_column(non_date_cols, col_width, return_format)
        column_headers = [index_label] + columns[:]
        for c in column_headers:
            worksheet.write(0, column_headers.index(c), c, header_format)
        return writer