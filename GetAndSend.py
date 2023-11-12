# -*- coding:utf-8 -*-
import requests

class GetSend():
    def getYiyan(self):
        try:
            # 语录
            content2all = ''
            types = ['a', 'b', 'c', 'd', 'f', 'h', 'i', 'j', 'k']
            for i in types:
                content2_url = f' https://v1.hitokoto.cn?c={i}'
                content2 = eval(requests.get(content2_url).text.replace('null', '""'))
                content2 = f'{content2["hitokoto"]}  --{content2["from_who"]}《{content2["from"]}》'
                content2all += content2 + '\n'
            return content2all
        except:
            return "每日一言获取失败"

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
                news += weiyu
                return news
        except:
            return "每天60秒读懂世界获取失败"

    def summary(self):
        try:
            # 获取推送内容
            sentence = self.getYiyan()
            news = self.get60s()
            # 汇总
            content = f'{sentence}\n{news}'
            return content
        except:
            return '今日推送获取失败'