from .base import IexApi
import pandas as pd, datetime as dt
from .pretty_json import prettyJson as pj

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

IEX = IexApi()

class Price:
    def __init__(self, symbols, output_path):
        self.symbols = symbols
        self.output_path = output_path
        self.save_data(self.request_data())
    def request_data(self):
        request = {
            'base_endpoint': 'stock',
            'symbols': self.symbols,
            'endpoints': ['price'],
            'other_options': {},
        }
        return IEX.get_data(request)
    def save_data(self, response_data):
        df = self.create_df(response_data)
        file_name = 'prices_factvest'
        self.save_to_excel(file_name, self.output_path, df)
    def create_df(self, response_data):
        columns = ['price']
        index = []
        df_data = []
        for stock_price in response_data:
            index.append(stock_price['symbol'])
            df_data.append({
                'price': stock_price['info']['price']
            })
        df = pd.DataFrame(data=df_data, columns=columns, index=index)
        return df
    def save_to_excel(self, file_name, output_path, df):
        columns = list(df.columns.values)
        info = {'sheet_name':'price', 'index_label':'symbol'}
        file_path = '{}\\{}.xlsx'.format(self.output_path, file_name)
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        df.to_excel(writer, **info)
        new_writer = self.format_csv(
            writer, columns,
            13.57, **info
        )
        new_writer.save()
        print('\tDone saving file | {}'.format(file_name))
    def format_csv(self, writer, columns, col_width, sheet_name, index_label):
        column_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        last_col = column_letters[len(columns)]
        used_column_letters = "A:" + last_col
        non_date_cols = "B:" + last_col
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
        col_1_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
        })
        price_format = workbook.add_format({
            'align': 'right',
            'indent': 1,
            'valign': 'vcenter',
            'num_format': '0.00'
        })


        worksheet.set_row(0, 22.5)
        worksheet.set_column(0, 0, cell_format=col_1_format)
        worksheet.set_column(non_date_cols, col_width, price_format)
        column_headers = [index_label] + columns[:]
        for c in column_headers:
            worksheet.write(0, column_headers.index(c), c, header_format)
        return writer