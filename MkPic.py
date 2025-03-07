"""
    function: 使用dataframe，生成图片
    author: SongChengXuan
    create time: 2022-09-01
"""
import plotly.graph_objects as go

from DateGet import getData


def mkPic(dlist):
    # 给首行着色
    headerColor = 'lightblue'
    # 给奇数偶数行制定不同的颜色
    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'

    fig = go.Figure(data=[go.Table(
        header=dict(
            # 制定列名称
            values=['<b>EXPENSES</b>', '<b>Qasim</b>', '<b>Hashim</b>', '<b>Sayim</b>', '<b>Qayim</b>'],
            line_color='darkslategray',
            fill_color=headerColor,
            align=['left', 'center'],
            font=dict(color='Black', size=16)
        ),
        cells=dict(
            values = dlist,
            # values=[
            #     ['Salaries', 'Office', 'Merchandise', 'Legal', '<b>TOTAL</b>'],
            #     [1200000, 20000, 80000, 2000, 12120000],
            #     [1300000, 20000, 70000, 2000, 130902000],
            #     [1300000, 20000, 120000, 2000, 131222000],
            #     [1400000, 20000, 90000, 2000, 14102000]],
            line_color='darkslategray',
            # 2-D list of colors for alternating rows
            fill_color=[[rowOddColor, rowOddColor, rowOddColor, rowOddColor, rowEvenColor] * 5],
            align=['left', 'center'],
            font=dict(color='darkslategray', size=12)
        ))
    ])
    # fig.show()
    # 保存图像
    fig.write_image("./pictures/Fig1.jpg", width=1920, height=1080, engine='kaleido')

# 主函数入口
if __name__ == '__main__':
    df = getData()
    dlist = [df.columns.tolist()]+df.values.tolist()
    mkPic(dlist)
