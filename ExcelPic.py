# -*- coding: utf-8 -*-
import time
from win32com.client import DispatchEx
import pythoncom
from PIL import ImageGrab
import datetime


# 函数功能：截取excel文件多个区域，生成对应多个.PNG图片
# 参数说明：
# filename：excel文件名（包括完整路径）
# sheetname：excel文件的sheet页名称
# screen_area：截图区域，以列表形式存储。取值例如：['A1:M11','A13:L23','A26:L36']，表示分别截取3个区域：A1到M11、A13到L23、A26到L36
# picture_name：生成截图的文件名（包括完整路径），以列表形式存储，程序会加上.PNG后缀。取值例如：['E:/pic1','E:/pic2','E:/pic3']
# flag：是否需要继续处理的标记，Y表示中间出现异常，没有生成全部截图，需要再调用此函数，处理未生成的截图；N表示全部处理完成
def excel_catch_screen(filename, sheetname, screen, picture):
    try:
        pythoncom.CoInitialize()  # excel多线程相关

        excel = DispatchEx("Excel.Application")  # 启动excel
        excel.Visible = True  # 可视化
        excel.DisplayAlerts = False  # 是否显示警告

        wb = excel.Workbooks.Open(filename)  # 打开excel
        time.sleep(5)
        ws = wb.Sheets(sheetname)  # 选择sheet
        # 处理截图区域
        ws.Range(screen).CopyPicture()  # 复制图片区域
        ws.Paste()  # 粘贴
        time.sleep(3)
        excel.Selection.ShapeRange.Name = picture  # 将刚刚选择的Shape重命名，避免与已有图片混淆
        ws.Shapes(picture).Copy()  # 选择图片
        time.sleep(3)
        img = ImageGrab.grabclipboard()  # 获取剪贴板的图片数据
        img_name = picture + ".PNG"  # 生成图片的文件名
        img.save(img_name)  # 保存图片
        flag = 'N'  # 如果程序执行到这里，说明所有截图都正常处理完成，将flag置为N
    except Exception as e:
        flag = 'Y'  # 只要有任一截图异常，退出当前程序，将flag置为Y，等待再次调用此函数
        print('error is:', e)  # 打印异常日志
    finally:
        wb.Close(SaveChanges=0)  # 关闭工作薄，不保存
        excel.Quit()  # 退出excel
        pythoncom.CoUninitialize()
    return flag


# 调用截图函数excel_catch_screen的入口
def gen(filename, sheetname, screen, picture):
    try:
        flag = 'Y'
        times = 0
        while flag == 'Y':  # 循环调用截图函数
            flag = excel_catch_screen(filename, sheetname, screen, picture)
            times += 1
            if times == 3: break
    except Exception as e:
        print('main error is:', e)
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' : 截图结束')


if __name__ == "__main__":
    # 配置区域
    filename = 'C:\code\PyCharmProject\WechatSend\excel\\7_MainProduct.xlsx'  # excel文件名
    sheetname = 'Table'  # excel文件的sheet页名称
    area = 'B1:S20'  # 截图区域
    picture = 'C:\code\PyCharmProject\WechatSend\pictures\\7_MainProduct'  # 生成截图的文件名
    print(filename, sheetname, area, picture)
    gen(filename, sheetname, area, picture)
