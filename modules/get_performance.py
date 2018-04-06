import money
from pretty_json import prettyJson as pj

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

# These functions are specific for getting key stats from securities
def handle_key_stats(raw_data, api_request):
    df_obj = create_stats_df(raw_data)
    df = df_obj['df']
    columns = df_obj['columns']
    file_name = '{}_stats'.format(api_request['folder']).lower()
    save_key_stats_excel(file_name, api_request['folder'], df, columns)
def save_key_stats_excel(file_name, folder, df, columns):
    sheet_name="data"
    index_label="symbol"
    file_path = 'Data\\{}\\{}.xlsx'.format(folder, file_name)
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name, index_label=index_label)
    new_writer = format_def_workbook(
        writer, columns,
        13.57, sheet_name,
        index_label,
        custom_stats_format
    )
    new_writer.save()
    print('done saving file | {}'.format(file_name))
def create_stats_df(all_data):
    index_column = []
    dataframe_data = []
    columns = ['5 day chg', '1 month chg', '3 month chg', '1 year chg', '5 year chg']

    for company in all_data:
        index_column.append(company['symbol'])
        stats = company['info']['stats']

        row = {
            '5 year chg': stats['year5ChangePercent'],
            '1 year chg': stats['year1ChangePercent'],
            '3 month chg': stats['month3ChangePercent'],
            '1 month chg': stats['month1ChangePercent'],
            '5 day chg': stats['day5ChangePercent']
        }
        dataframe_data.append(row)

    df = pd.DataFrame(data=dataframe_data, columns=columns, index=index_column)
    return {'df': df, 'columns': columns}
def custom_stats_format(workbook, writer, worksheet):
    return_format = workbook.add_format({
        'num_format': '0.00%',
        'align': 'right',
        'valign': 'vcenter',
        'indent': 1,
    })

    worksheet.set_column('B:F', None, return_format)
