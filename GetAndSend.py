# -*- coding:utf-8 -*-
import requests

class GetSend():
    def get60s(self):
        try:
            news_url = 'https://v2.alapi.cn/api/zaobao?token=BjEDPZdub0XZflvL&format=json'
            response = requests.get(news_url).json()
            if response['code'] == 200:
                data = response['data']['news']
                weiyu = response['data']['weiyu']
                news = f'\n  每天60秒读懂世界\n'
                for i in data:
                    news += i + '\n'
                news += '\n' + weiyu
                return news
        except:
            return "每天60秒读懂世界获取失败"
    def summary(self):
        try:
            news = self.get60s()
            return news
        except:
            return '今日推送获取失败'