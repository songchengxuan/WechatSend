"""
    function: 读取数据库数据，整理成df
    author: SongChengXuan
    create time: 2022-08-31
    ps: 方法1——将数据写入一个新建的excel中，另一个excel作为模板读取这个excel形成报表，再用软件读取模板excel，并截图发表
        方法2——将数据写入同一个excel中，该excel里面有底表有模板，之后同上
        方法3——直接将数据写入模板excel中，之后同上
"""
import time
from datetime import datetime
from openpyxl import load_workbook
import psycopg2
import psycopg2.extras
import pandas as pd
from ConfigRead import configRead_corr_days, configRead_sql

# 连接数据库
def gp_connect():
    try:
        db = psycopg2.connect(dbname="hodo_dw",
                              user="etl",
                              password="Asd123123`",
                              host="10.10.67.160",
                              port="5432")
        # connect()也可以使用一个大的字符串参数,
        # 比如”host=localhost port=5432 user=postgres password=postgres dbname=test”
        print("connect to Greenplum server success")
        return db
    except psycopg2.DatabaseError as e:
        print("could not connect to Greenplum server", e)

# df写入新建excel
def excelInsert(df, fromcol, fromrow, file, tabname):
    # 建立写入对象
    book = load_workbook(file)
    write = pd.ExcelWriter(file, engine='openpyxl')
    write.book = book
    write.sheets = {ws.title: ws for ws in book.worksheets}
    # header=0: 表示第0行为表头，第0行之前的数据不保留
    # header=None: 不设置表头
    # index=False: 不保留索引
    df.to_excel(write,
                sheet_name=tabname,
                header=0,
                index=False,
                startcol=fromcol,
                startrow=fromrow,
                float_format='%.2f'
                )
    time.sleep(3)
    write.save()
    write.close()

# 数据读取
class getDataC():
    start_time = datetime.now()

    def __init__(self, cur, ret_sql, table_name):
        self.cur = cur
        self.ret_sql = ret_sql
        self.table_name = table_name

    def collect(self):
        # 开始查询
        self.cur.execute(self.ret_sql)
        gp_list = self.cur.fetchall()
        # 将获得的列名元组数据转换为dataframe
        columnDes = self.cur.description  # 获取连接对象的描述信息
        columnNames = [columnDes[i][0] for i in range(len(columnDes))]
        df = pd.DataFrame([list(i) for i in gp_list], columns=columnNames)
        return df

    def handleData(self):
        # 字符串转换
        df = self.collect()
        return df

    def showData(self):
        print("=====", self.table_name, "======")
        df = self.handleData()
        print('查询数据所用时间:', (datetime.now() - self.start_time).seconds, 's')
        print('数据表行数：', df.shape[0])
        print(df.head(1))
        return df


class ChildOne(getDataC):
    def handleData(self):
        df = self.collect()
        df['business_amount'] = df['business_amount'].astype(float)
        df['tag_price'] = df['tag_price'].astype(float)
        return df

class ChildTwo(getDataC):
    def handleData(self):
        df = self.collect()
        df['business_amount'] = df['business_amount'].astype(float)
        return df

class ChildFour(getDataC):
    def handleData(self):
        df = self.collect()
        df['business_amount'] = df['business_amount'].astype(float)
        df['business_amount_percentage'] = df['business_amount_percentage'].astype(float)
        return df


# 数据汇总
def getData():
    pd.set_option('display.unicode.east_asian_width', True)  # 列名与值对齐
    pd.set_option('display.max_columns', None)  # 设置None则无列数的显示限制
    pd.set_option('display.width', 1000)  # 不换行显示
    conn = gp_connect()
    cur = conn.cursor()
    ret_sql_1, ret_sql_2, ret_sql_3, ret_sql_4, ret_sql_5, ret_sql_6, ret_sql_7 = configRead_sql()
    corr_days = configRead_corr_days()

    para1 = ChildOne(cur, ret_sql_1, '连锁区域销售表')
    df1 = super(ChildOne, para1).showData()

    para2 = ChildTwo(cur, ret_sql_2, 'TOP50和BOTTOM50门店销售')
    df2 = super(ChildTwo, para2).showData()

    para3 = getDataC(cur, ret_sql_3, '部门主推销售')
    df3 = para3.showData()

    para4 = ChildFour(cur, ret_sql_4, '季节品类前七')
    df4 = super(ChildFour, para4).showData()

    para5 = ChildTwo(cur, ret_sql_5, '门店主推销售')
    df5 = super(ChildTwo, para5).showData()

    para6 = ChildTwo(cur, ret_sql_6, '小时时段销售')
    df6 = super(ChildTwo, para6).showData()

    para7 = getDataC(cur, ret_sql_7, '营业部主推销售')
    df7 = para7.showData()

    # para8 = ChildTwo(cur, ret_sql_8, '营业部长连带率及客单价')
    # df8 = super(ChildTwo, para8).showData()
    #
    # df9 = df8[["sdate", "branch_name", "org_org_department_id", "org_department_name", "business_amount", "business_qty", "nums_of_effective"]]\
    #     .groupby(["sdate", "branch_name", "org_org_department_id", "org_department_name"]).sum()
    # print("=====营业部长连带率及客单价2======")
    # print(df9.head(1))

    conn.close()  # 关闭数据库连接
    cur.close()  # 关闭游标
    # return df1
    return df1, df2, df3, df4, df5, df6, df7


# 主函数入口1
if __name__ == '__main__':
    getdatac = getDataC()

    # df1 = getData()
    # print(locals()['df'+str(1)])
    # filename = 'D:\code\PyCharmProject\WechatSend\excel\\1_DepartmentSales.xlsx'  # excel文件名
    # excelInsert(df1, 0, 1, filename, 'DataSheet')