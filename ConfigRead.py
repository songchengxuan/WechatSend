import yaml

with open('config.yaml', 'r', encoding='utf-8') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

corr_days = data["corr_days"]
excel_file_name = data["excel_file_name"]
excel_pic_start = data["excel_pic_start"]
excel_table_name = data["excel_table_name"]
excel_datasheet_name = data["excel_datasheet_name"]
excel_pic_area = data["excel_pic_area"]
send_pic_name = data["send_pic_name"]

ret_sql = [
    data["ret_sql_1"],
    data["ret_sql_2"],
    data["ret_sql_3"],
    data["ret_sql_4"],
    data["ret_sql_5"],
    data["ret_sql_6"],
    data["ret_sql_7"]
]


def configRead():
    return excel_file_name, \
           excel_pic_start, \
           excel_table_name, \
           excel_datasheet_name, \
           excel_pic_area, \
           send_pic_name


def configRead_sql():
    return ret_sql

def configRead_corr_days():
    return corr_days
