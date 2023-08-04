import os
import requests
import json
import datetime
import logging
import random
import time
from wxpusher import WxPusher
from GetAndSend import GetSend

TOMORROW = str(datetime.date.today() + datetime.timedelta(days=1))
fileloc = './log.txt'
client_path = "./clients"

logging.basicConfig(filename=fileloc, level=logging.DEBUG,
                    format=' %(asctime)s - %(levelname)s- %(message)s')
# wxpusher微信推送程序
appToken = ""
# 请求头
header = {
    # 设定报文头
    'Host': 'libzwxt.ahnu.edu.cn',
    'Origin': 'http://libzwxt.ahnu.edu.cn',
    'Referer': 'http://libzwxt.ahnu.edu.cn/SeatWx/Seat.aspx?fid=3&sid=1438',
    # 'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
    # 设置为安卓手机的请求头
    'User-Agent': "Mozilla/5.0 (Linux; Android 12; M2006J10C Build/SP1A.210812.016; wv) \
    AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5061 \
    MMWEBSDK/20230303 MMWEBID/534 MicroMessenger/8.0.34.2340(0x2800225D) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64;",
    'X-AjaxPro-Method': 'AddOrder',
    "Connection": "close",
}


# 程序随机睡眠 单位：秒
def randSleep(least, most):
    # 生成随机种子
    random.seed(time.time())
    second = random.randint(least, most)
    time.sleep(second)


def getClients(client_path):
    clients = []
    # 获取文件夹中的所有文件
    json_files = os.listdir(client_path)
    for json_name in json_files:
        with open(os.path.join(client_path, json_name)) as f:
            clients.append(json.load(f))
    return clients


class Reserve:
    def __init__(self, **kwargs):
        self.info = kwargs
        self.sid = 35
        self.session = requests.Session()

    def reserve(self):
        self.login()
        try:
            self.sid, whichone = self.convert(self.info['sid'])
            # 记录对应规则
            self.info['whichone'] = whichone
            if whichone == 0:
                logging.info("请输入正确的座位，只能预约2,3,4楼的自习室")
            # 开始预约
            logging.info('开始预约...')
            header = {
                # 设定报文头
                'Host': 'libzwxt.ahnu.edu.cn',
                'Origin': 'http://libzwxt.ahnu.edu.cn',
                'Referer': 'http://libzwxt.ahnu.edu.cn/SeatWx/Seat.aspx?fid=3&sid=1438',
                'User-Agent': "Mozilla/5.0 (Linux; Android 12; M2006J10C Build/SP1A.210812.016; wv) \
                AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36 XWEB/5061 \
                MMWEBSDK/20230303 MMWEBID/534 MicroMessenger/8.0.34.2340(0x2800225D) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64;",
                'X-AjaxPro-Method': 'AddOrder',
            }
            reserveUrl = 'http://libzwxt.ahnu.edu.cn/SeatWx/ajaxpro/SeatManage.Seat,SeatManage.ashx'
            reserverData = {
                'atDate': TOMORROW,
                'sid': self.sid,
                'st': TOMORROW + self.info['st'],
                'et': TOMORROW + self.info['et'],
            }
            # 预约时间延时10到15秒
            randSleep(10, 15)
            # 尝试进行预约
            reserve = self.session.post(reserveUrl, data=json.dumps(reserverData), headers=header)
            if '成功' in reserve.text:
                logging.info(reserve.text)
                logging.info('预约成功！座位号是 {0}'.format(self.info['sid']))
                winxin = WINXIN(self.info)
                winxin.send()

            if '预约成功' not in reserve.text:
                # 预约未成功，再次尝试
                # 预约时间延时10到15秒
                randSleep(10, 15)
                reserve = self.session.post(reserveUrl, data=json.dumps(reserverData), headers=header)

                # 服务器时间不一致
                if '提前' in reserve.text:
                    logging.warning(reserve.text)
                elif '冲突' or '重复' in reserve.text:
                    # 时间和其他人有冲突
                    logging.warning(reserve.text)
                    logging.warning('座位冲突，预约失败！')
                elif '二次' in reserve.text:
                    logging.info(reserve.text)
                elif '成功' in reserve.text:
                    # 预约完成
                    logging.info(reserve.text)
                    winxin = WINXIN(self.info)
                    winxin.send()
                    # break
                else:
                    logging.info(reserve.text)
                    logging.error('未知原因，未预约成功，请检查日志及数据设置！！！')

        except BaseException as e:
            logging.error(e)

    def login(self):
        logging.info('''
                    start  with 账号:{0}, 密码:{1}, 座位号:{2}. 从{3}到{4}.'''
                     .format(self.info['account'], self.info['password'], self.info['sid'], TOMORROW + self.info['st'],
                             TOMORROW + self.info['et']))

        # 开始登陆
        postUrl = 'http://libzwxt.ahnu.edu.cn/SeatWx/login.aspx'
        postData = {
            '__VIEWSTATE': '/wEPDwULLTE0MTcxNzMyMjZkZAl5GTLNAO7jkaD1B+BbDzJTZe4WiME3RzNDU4obNxXE',
            '__VIEWSTATEGENERATOR': 'F2D227C8',
            '__EVENTVALIDATION': '/wEWBQK1odvtBQLyj/OQAgKXtYSMCgKM54rGBgKj48j5D4sJr7QMZnQ4zS9tzQuQ1arifvSWo1qu0EsBRnWwz6pw',
            'tbUserName': self.info['account'],
            'tbPassWord': self.info['password'],
            'Button1': '登 录',
            'hfurl': ''
        }

        login = self.session.post(postUrl, data=postData)

        if '个人中心' in login.content.decode():
            logging.info('登录成功！')

    @staticmethod
    def convert(seat_code):  # nsk3004
        sid = 0
        # 记录是哪个规则映射的
        whichone = 0
        if seat_code[:3] == 'nzr':
            sid = int(seat_code[3:]) + 437
            whichone = 1
        elif seat_code[:3] == 'nsk' and seat_code[3] == '1':
            sid = int(seat_code[3:]) + 95
            whichone = 2
        elif seat_code[:3] == 'nsk' and seat_code[3] == '3':
            sid = int(seat_code[3:]) - 2477
            whichone = 3
        elif seat_code[:3] == 'nsk' and seat_code[3] == '2':
            sid = int(seat_code[3:]) - 1177
            whichone = 4
        elif seat_code[:3] == 'nbz':
            sid = int(seat_code[3:])
            whichone = 5
        elif seat_code[:3] == 'nbk':
            sid = int(seat_code[3:])
            whichone = 6
        elif seat_code[:3] == 'ndz':
            sid = int(seat_code[3:]) + 2875
            whichone = 7
        # 三楼公共阅览室东
        elif seat_code[:5] == 'ngg3e':
            number = int(seat_code[5:])
            if number < 89:
                sid = number + 2433
                whichone = 8
            else:
                sid = number - 89 + 2682
                whichone = 9
        elif seat_code[:5] == 'ngg3w':
            number = int(seat_code[5:])
            sid = number + 2521
            whichone = 10
        elif seat_code[:5] == 'ngg4e':
            number = int(seat_code[5:])
            if number < 33:
                sid = number + 2617
                whichone = 11
            else:
                sid = number - 33 + 2754
                whichone = 12
        elif seat_code[:5] == 'ngg4w':
            number = int(seat_code[5:])
            if number < 33:
                sid = number + 2649
                whichone = 13
            elif 33 <= number <= 96:
                sid = number - 33 + 2690
                whichone = 14
            else:
                sid = number - 97 + 3143
                whichone = 15
        return sid, whichone


class WINXIN:
    def __init__(self, kwargs):
        self.INFO = kwargs

    def send(self):
        # 推送内容
        if self.INFO['account'] == '20112001120':
            nickname = '丘~~~~~'
        elif self.INFO['account'] == '20111304054':
            nickname = '超超~~~~~~'
        elif self.INFO['account'] == '20111701089':
            nickname = '铮~~~~~'
        else:
            nickname = self.INFO['account']
        # 座位号
        seatid = self.INFO['sid']
        # 每日一句
        daily = GetSend()
        dailyContent = daily.summary()

        content = f"{nickname}\n\n您明天的座位已经预约完成！\n预约座位编号：{seatid}\n预约时间：{self.INFO['st']}~{self.INFO['et']}\n\n{dailyContent}"
        WxPusher.send_message(
            content=content,
            summary='预约座位信息',
            uids=self.INFO['uids'],
            token=appToken,
            topic_ids=[]
        )
        logging.info('消息已发出')


if __name__ == '__main__':
    randSleep(180, 480)
    clients = getClients(client_path)
    try:
        for i in range(len(clients)):
            randSleep(60, 120)
            reserve = Reserve(**clients[i])
            reserve.reserve()
    finally:
        push1 = GetSend()
        push1.msgPush()
