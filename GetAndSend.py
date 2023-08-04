# -*- coding:utf-8 -*-
import datetime
import time
import json
import random

import requests
from wxpusher import WxPusher

# wxpusher用到
appToken = ""
our_uids = [
    ""
]
# 每日推送功能中用到
app_id = ''
app_secret = ''
headers = {
    'app_id': app_id,
    'app_secret': app_secret
}


class GetSend():
    def getSentence(self):
        with open('./infos/名人名言.json', 'r', encoding='utf-8') as f:
            sentences = json.load(f)
        ran_sentence = random.randint(0, len(sentences) - 1)
        sentence = sentences[ran_sentence]
        return '每日名言：' + sentence

    def getHistory(self):
        time.sleep(1)
        history_url = ' https://www.mxnzp.com/api/history/today'  # 接口地址
        response = requests.get(history_url, headers=headers)
        res_data = response.json()  # 解析返回的 JSON 数据
        if res_data['code'] == 1:  # 判断请求是否成功，具体根据返回数据格式进行调整
            text = res_data['data'][0]
            content = f'历史上的今天：\n{text["year"]} 年 {text["month"]} 月 {text["day"]} 日 {text["title"]}。'
            return content

    def getWeather(self, city):
        time.sleep(1)
        weather_url = f' https://www.mxnzp.com/api/weather/current/{city}'
        response = requests.get(weather_url, headers=headers)
        res_data = response.json()
        if res_data['code'] == 1:
            mes = res_data['data']
            content = f'{mes["address"]} 当前气温{mes["temp"]} 天气{mes["weather"]} ' \
                      f'{mes["windDirection"]}风{mes["windPower"]} 空气湿度{mes["humidity"]}'
            return content

    def getCalendar(self):
        time.sleep(1)
        today = datetime.date.today()
        formatted_date = today.strftime("%Y%m%d")
        weather_url = f' https://www.mxnzp.com/api/holiday/single/{formatted_date}'
        response = requests.get(weather_url, headers=headers)
        res_data = response.json()
        if res_data['code'] == 1:
            mes = res_data['data']
            content = f'今天是{mes["yearTips"]}年 {mes["lunarCalendar"]} \n忌：{mes["avoid"]}\n宜：{mes["suit"]}\n' \
                      f'阳历今年第{mes["dayOfYear"]}天，第{mes["weekOfYear"]}周'
            return content

    def getNews(self):
        time.sleep(1)
        params = {"typeId": 532, "page": 1}
        content = '每日新闻：'
        newslist_url = f' https://www.mxnzp.com/api/news/list/v2'
        response = requests.get(newslist_url, params=params, headers=headers)
        res_data = response.json()
        # 新闻返回成功
        if res_data['code'] == 1:
            # 随机挑选一个新闻
            rand = random.randint(0, len(res_data['data']) - 1)
            choosed = res_data["data"][rand]
            # 提取出新闻的标题、来源和实践
            content += choosed["title"] + '\n' + choosed["source"] + ' ' + choosed["postTime"] + '\n'
            newsid = choosed["newsId"]
            # 延迟一秒再发送
            time.sleep(1)
            news_url = f'https://www.mxnzp.com/api/news/details/v2'
            response = requests.get(news_url, params={"newsId": newsid}, headers=headers)
            detail_data = response.json()
            if detail_data['code'] == 1:
                for item in detail_data['data']["items"]:
                    if item["type"] == "text":
                        content += item["content"] + '\n'
            return content

    def summary(self, uids=our_uids):
        sentence = self.getSentence()  # 获取每日一句
        history = self.getHistory()  # 获取历史上的今天

        # 获取今日天气
        weather = self.getWeather('芜湖市')
        if len(uids) == 2:
            weather2 = self.getWeather('翁源')
            weather = weather + '\n' + weather2
        # 获取万年历
        calendar = self.getCalendar()
        # 获取今日新闻
        news = self.getNews()
        # 汇总
        content = f'{sentence}\n\n{calendar} \n\n{weather}\n\n{history}\n\n{news}'
        return content

    def msgPush(self):
        content = self.summary()
        WxPusher.send_message(
            content=content,
            summary='预约座位信息',
            uids=our_uids,
            token=appToken,
            topic_ids=[]
        )
