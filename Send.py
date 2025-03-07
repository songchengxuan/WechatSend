'''
    function: 发送保存好的图像到微信窗口
    author: SongChengXuan
    create time: 2022-09-02
    wechat address：xxx
'''
import requests
import base64
import hashlib


# 文本类型消息
def send_msg_txt(text):
    headers = {"Content-Type": "text/plain"}
    send_url = "xxx"
    send_data = {
        "msgtype": "text",  # 消息类型，此时固定为text
        "text": {
            "content": text,  # 文本内容，最长不超过2048个字节，必须是utf8编码
            # "mentioned_list": ["@all"],
            # userid的列表，提醒群中的指定成员(@某个成员)，@all表示提醒所有人，如果开发者获取不到userid，可以使用mentioned_mobile_list
            # "mentioned_mobile_list": ["@all"]  # 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
        }
    }
    res = requests.post(url=send_url, headers=headers, json=send_data)
    print(res.text)

def send_image_message(picpath):
    with open(picpath,'rb') as f:
        # 转换图片为base64格式
        base64_data = base64.b64encode(f.read())
        image_data = str(base64_data,'utf-8')
    with open(picpath,'rb') as f:
        # 获取图片的md5值
        md = hashlib.md5()
        md.update(f.read())
        image_md5 = md.hexdigest()
    # 企业微信机器人发送图片消息
    url = 'xxx'
    headers = {"Content-Type":'application/json'}
    data = {
        'msgtype': 'image',
        'image': {
            'base64': image_data,
            'md5': image_md5
        }
    }
    # 发送请求
    r = requests.post(url,headers=headers,json=data)
    print(r, '图片发送成功')

# 主函数入口
if __name__ == '__main__':
    picpath = './pictures/Fig.jpg'
    send_image_message(picpath)
