import os
import requests
import json
import datetime
import logging
import random
import time
from wxpusher import WxPusher
from GetAndSend import GetSend

# wxpusher微信推送程序
appToken = ""

TOMORROW = str(datetime.date.today() + datetime.timedelta(days=1))
fileloc = 'log.txt'
client_path = "./clients"

logging.basicConfig(filename=fileloc, level=logging.DEBUG,
                    format=' %(asctime)s - %(levelname)s- %(message)s')
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


# 程序随机睡眠 单位：秒
def randSleep(least, most):
    # 生成随机种子
    random.seed(time.time())
    second = random.randint(least, most)
    time.sleep(second)
    logging.info(f'Delayed by {second} second randomly!')


def getClients(client_path):
    clients = []
    # 获取文件夹中的所有文件
    json_files = os.listdir(client_path)
    for json_name in json_files:
        if os.path.splitext(json_name)[1] == '.json':
            with open(os.path.join(client_path, json_name)) as f:
                clients.append(json.load(f))
    return clients


class Reserve:
    def __init__(self, **kwargs):
        self.info = kwargs
        self.sid = 35  # 将座位号对应的sid定义到类内
        self.session = requests.Session()

    def reserve(self):
        self.login()
        try:
            self.sid = self.convert(self.info['sid'])
            # 开始预约
            logging.info('Begin to reserve...')
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
                logging.info('Booking successful! The seat number is {0}\n'.format(self.info['sid']))
                winxin = WINXIN(self.info)
                winxin.send()

            if '预约成功' not in reserve.text:
                # 服务器时间不一致
                if '提前' in reserve.text:
                    logging.info('Not at the scheduled time!')
                if '冲突' or '重复' in reserve.text:
                    logging.warning('Seat conflict, booking failed!')
                if '二次' in reserve.text:
                    logging.info('Your second booking time interval is too short!')
                if '提前' not in reserve.text and '冲突' not in reserve.text and '重复' not in reserve.text and '二次' not in reserve.text:
                    logging.error('Unknown reason, booking unsuccessful, please check the logs and data settings!!!')

        except BaseException as e:
            logging.error(e)

    def login(self):
        logging.info('''
                    start  with account: {0}, password: {1}, seatid: {2}. From {3} to {4}.'''
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
            'Button1': '登 录  ',
            'hfurl': ''
        }

        login = self.session.post(postUrl, data=postData, headers=header)

        if '个人中心' in login.content.decode():
            logging.info('Login successful!')
        else:
            logging.info('Login failed!')

    @staticmethod
    def convert(seat_code):  # nsk3004
        """
        :param seat_code: str like "nsk3004"
        :return: sid converted by seated
        """
        sid = 0
        if seat_code[:3] == 'nzr':
            sid = int(seat_code[3:]) + 437
        elif seat_code[:3] == 'nsk' and seat_code[3] == '1':
            sid = int(seat_code[3:]) + 95
        elif seat_code[:3] == 'nsk' and seat_code[3] == '3':
            sid = int(seat_code[3:]) - 2477
        elif seat_code[:3] == 'nsk' and seat_code[3] == '2':
            sid = int(seat_code[3:]) - 1177
        elif seat_code[:3] == 'nbz':
            sid = int(seat_code[3:])
        elif seat_code[:3] == 'nbk':
            sid = int(seat_code[3:])
        elif seat_code[:3] == 'ndz':
            sid = int(seat_code[3:]) + 2875
        # 三楼公共阅览室东
        elif seat_code[:5] == 'ngg3e':
            number = int(seat_code[5:])
            if number < 89:
                sid = number + 2433
            else:
                sid = number - 89 + 2682
        elif seat_code[:5] == 'ngg3w':
            number = int(seat_code[5:])
            sid = number + 2521
        elif seat_code[:5] == 'ngg4e':
            number = int(seat_code[5:])
            if number < 33:
                sid = number + 2617
            else:
                sid = number - 33 + 2754
        elif seat_code[:5] == 'ngg4w':
            number = int(seat_code[5:])
            if number < 33:
                sid = number + 2649
            elif 33 <= number <= 96:
                sid = number - 33 + 2690
            else:
                sid = number - 97 + 3143
        return sid


class WINXIN:
    def __init__(self, kwargs):
        self.INFO = kwargs

    def send(self):
        nickname = self.INFO['account']
        # 座位号
        seatid = self.INFO['sid']

        try:
            # 每日一句
            daily = GetSend()
            dailyContent = daily.summary()
            content = f"{nickname}明天的座位{seatid}预约成功！\n预约时间：{TOMORROW + self.INFO['st']}~{self.INFO['et']}\n\n{dailyContent}"
        except:
            content = f"{nickname}明天的座位{seatid}预约成功！\n预约时间：{self.INFO['st']}~{self.INFO['et']}"
            logging.info('Failed to retrieve daily push, please check the log and code for error details!\n')
        try:
            WxPusher.send_message(
                content=content,
                summary='预约座位信息',
                uids=self.INFO['uids'],
                token=appToken,
                topic_ids=[]
            )
            logging.info('Message of successful appointment has been sent!')
        except:
            logging.info('Message sending failed, appToken may not be configured.')


if __name__ == '__main__':
    # 预约部分
    randSleep(120, 420)
    clients = getClients(client_path)
    random.shuffle(clients)  # 打乱数组顺序
    try:
        for i in range(len(clients)):
            try:
                randSleep(60, 240)
                reserve = Reserve(**clients[i])
                reserve.reserve()
            except:
                logging.info(f'Account {clients[i]["account"]} failed to reserve...reason unkown')
        logging.info('Today\'s appointment booking is over.\n\n\n\n\n')
    except:
        logging.error('Appointment code execution failed, reason unknown.')
