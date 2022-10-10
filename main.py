from flask import Flask, request, abort
#置入line bot api
from linebot import (
    LineBotApi, WebhookHandler
)
#python使用requests模組產生http請求
import requests
#使用json(為內建，不需pip install)
import json;
#使用line bot api時發生錯誤使用的exception
from linebot.exceptions import (
    InvalidSignatureError
)
#要使用line bot api內的甚麼功能(現在是全不):MessageEvent,TextMessage,TextSendMessage
from linebot.models import *

#使用flask package當中的功能創建一個flask框架並命名為app
app = Flask(__name__)

#要使用line bot需要進行的驗證程序
# LINE BOT info
line_bot_api = LineBotApi('TkG0zfhlutudYYwK2nW6kBdw6GSJ1wGQJyRMrRx+EuQmTHyrgCmGMYo81Cz5hwgLvk723Ikzy5yUSfcjrxnUsgIuw3MDXWCjnkzelqYJqUHF7LuK/4hNujFAisuMKgFZHYS2lpK70BtAn/GlEVHsogdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('24b6475f17d23cea80b5348be59fb714')

#放置我的function
def getcity(city):
    #從氣象網站抓下來我的token
    token = 'CWB-25B9217E-61DB-4600-ADB1-97D5E90935E1' 
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + token + '&format=JSON&locationName=' + str(city)
    #我要擷取出來的資料為:天氣現象、最高最低溫度、降雨機率
    Data = requests.get(url)
    #將json格式轉化成python dictionary格式
    Data = (json.loads(Data.text))['records']['location'][0]['weatherElement']
    res = [[] , [] , []]
    for j in range(3):                                                                                          
       for i in Data:
           res[j].append(i['time'][j])
    return res

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# Message event
@handler.add(MessageEvent)
def handle_message(event):
    #基本linebot設定
    message_type = event.message.type
    user_id = event.source.user_id
    reply_token = event.reply_token
    message = event.message.text
    #設定有哪些縣市
    cities=[
            "宜蘭縣","花蓮縣","臺東縣",
            "澎湖縣","金門縣","連江縣",
            "臺北市","新北市","桃園市",
            "臺中市","臺南市","高雄市",
            "基隆市","新竹縣","新竹市",
            "苗栗縣","彰化縣","南投縣",
            "雲林縣","嘉義縣","嘉義市",
            "屏東縣"
        ]
    #處理輸入資料
    if(message[:2] == '天氣'):
        city = message[3:]
        city = city.replace('台','臺')
        # 使用者輸入的內容並非符合格式
        if(not (city in cities)):
            line_bot_api.reply_message(reply_token,TextSendMessage(text="查詢格式為: 天氣 縣市"))
        else:
        # 處理輸出
            res = getcity(city)
            line_bot_api.reply_message(reply_token, TemplateSendMessage(
                alt_text = city + '未來 36 小時天氣預測',
                template = CarouselTemplate(
                    columns = [
                        CarouselColumn(
                            thumbnail_image_url = "https://ibb.co/m8VMPWW",
                            title = '{} ~ {}'.format(data[0]['startTime'][5:-3],data[0]['endTime'][5:-3]),
                            text = '天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(data[0]['parameter']['parameterName'],data[2]['parameter']['parameterName'],data[4]['parameter']['parameterName'],data[1]['parameter']['parameterName']),
                            actions = [
                                URIAction(
                                    label = '詳細內容',
                                    uri = 'https://www.cwb.gov.tw/V8/C/W/County/index.html'
                                )
                            ]
                        )for data in res
                    ]
                )
            ))
    else:
        line_bot_api.reply_message(reply_token,TextSendMessage(text="查詢格式為: 天氣 縣市"))
#抓取網站資料   

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)