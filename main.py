"""
    function: 读取数据库数据，形成图片，并发送到企微指定联系人
    author: SongChengXuan
    create time: 2022-08-31
"""
import sys

from ConfigRead import configRead

sys.path.extend(['C:\\code\\PyCharmProject\\WechatSend\\venv\\Lib\\site-packages'])
sys.path.append('../..')

import os
import shutil
import time
from glob import glob
from DateGet import excelInsert, getData
from ExcelPic import gen
from Send import send_image_message, send_msg_txt


# srcfile 需要复制、移动的文件
# dstpath 目的地址

def mycopyfile(srcfile, dstpath):  # 复制函数
    if not os.path.isfile(srcfile):
        print("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(srcfile)  # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建路径
        shutil.copy(srcfile, dstpath + fname)  # 复制文件
        print("copy %s -> %s" % (srcfile, dstpath + fname))


# 删除文件夹下所有文件【类似unix下的 rm -r aa/bb】
def rmDirAllFiles(dstDir):
    lists = os.listdir(dstDir)
    for lt in lists:
        srcPath = os.path.join(dstDir, lt)
        if os.path.isfile(srcPath):
            os.remove(srcPath)
        else:
            shutil.rmtree(srcPath)


def send_pic(df, fromcol, fromrow, filename, tabname, sheetname, area_list, picture_list, table_send, table_send_error):
    try:
        excelInsert(df, fromcol, fromrow, filename, tabname)
        gen(filename, sheetname, area_list, picture_list)
        send_image_message(picture_list + '.PNG')
        table_send += 1
    except Exception as e:
        print('error is:', e)  # 打印异常日志
        table_send_error += 1
    finally:
        time.sleep(3)
    return table_send, table_send_error


def task():
    # 读取配置
    excel_file_name, \
    excel_pic_start, \
    excel_table_name, \
    excel_datasheet_name, \
    excel_pic_area, \
    send_pic_name = configRead()
    # 读取数据
    # df1, df2, df3, df4, df5, df6, df7 = getData()
    df1 = getData()
    # 更新文件
    for i in range(0, len(send_pic_name)):
        try:
            os.remove(send_pic_name[i] + '.PNG')
        except Exception as e:
            print('error is:', e)  # 打印异常日志

    send_msg_txt('''
    [拥抱]报表小助手提示您：
    整点报表开始发送
    [转圈]当前时间%s
    ''' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    table_send = 0
    table_send_error = 0

    for i in range(0, len(excel_file_name)):
        table_send, table_send_error = send_pic(
            locals()['df'+str(i+1)],
            excel_pic_start[i][0],
            excel_pic_start[i][1],
            excel_file_name[i],
            excel_datasheet_name,
            excel_table_name,
            excel_pic_area[i],
            send_pic_name[0],
            table_send,
            table_send_error)

    send_msg_txt('''
    [拥抱]报表小助手提示您：
    整点报表发送结束
    成功发送%s,失败%s张
    ''' % (table_send, table_send_error))


# 主程序入口
if __name__ == '__main__':
    print('程序开始运行')
    # 判断时间
    Judge_Time = time.strftime("%Y-%m-%d 11:00:00", time.localtime())
    # 当前时间
    Current_Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if Current_Time > Judge_Time:
        try:
            src_dir = 'C:/code/PyCharmProject/WechatSend/excel_base/'
            dst_dir = 'C:/code/PyCharmProject/WechatSend/excel/'
            src_file_list = glob(src_dir + '*')
            for src_file in src_file_list:
                mycopyfile(src_file, dst_dir)
        except Exception as e:
            print('error is:', e)  # 打印异常日志
        finally:
            print('替换文件完成')
            task()
    else:
        print('直接运行')
        task()
