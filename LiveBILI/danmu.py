#bilibili直播弹幕服务器操作
from Log import ERROR,INFO
from struct import Struct
from threading import Thread
import zlib
import time
import json
import requests
import websocket
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

#实例化一个调度器
scheduler = BackgroundScheduler()
def tick():
    jobs = scheduler.get_jobs()
    INFO(f'现在心跳任务数量：{len(jobs)}')

scheduler.add_job(tick, 'interval', hours=1 )
scheduler.start()

class Danmu:
    header_struct = Struct('>I2H2I')
    def __init__(self,roomid:int) -> None:
        if roomid < 5000:
            '''小于5000的默认他是短号'''
            print('短号转换')
            self.roomid,self.uid = self.Getroomid_uid(roomid)
        else:
            self.roomid = roomid
            self.uid = 0
        self.job = None
        self.func = {
        'DANMU_MSG':self.OnDANMU_MSG,
        'LIVE':self.OnLIVE,
        'PREPARING':self.OnPREPARING,
        'SEND_GIFT':self.OnGIFT,
        'ROOM_CHANGE':self.OnCHANGE,
        'CUT_OFF':self.OnCUT_OFF,
        'ANCHOR_LOT_START':self.OnANCHOR_LOT_START,
        'ANCHOR_LOT_AWARD':self.OnANCHOR_LOT_AWARD,
        'GUARD_BUY':self.OnGUARD_BUY,
        'VOICE_JOIN_STATUS':self.OnVOICE_JOIN_STATUS,
        'WARNING':self.OnWARNING,
        'INTERACT_WORD':self.OnINTERACT_WORD
    }
    def OnDANMU_MSG(self,data):
        '''收到弹幕消息'''
    def OnLIVE(self,data):
        '''开播调用'''
    def OnPREPARING(self,data):
        '''下播调用'''
    def OnGIFT(self,data):
        '''收到礼物'''
    def OnCHANGE(self,data):
        '''房间信息：修改标题，修改分区'''
    def OnCUT_OFF(self,data):
        '''房间被切'''
    def OnANCHOR_LOT_START(self,data):
        '''天选时刻抽奖开始'''
    def OnANCHOR_LOT_AWARD(self,data):
        '''天选时刻中间信息'''
    def OnVOICE_JOIN_STATUS(self,data):
        '''连麦'''
    def OnGUARD_BUY(self,data):
        '''舰队'''
    def OnWARNING(self,data):
        '''收到警告'''
    def OnINTERACT_WORD(self,data):
        '''用户进入直播间'''
    def Onother(self,data):
        '''其他消息'''

    def Getroomid_uid(self,roomid):
        '''获取长号和uid'''
        url = 'https://api.live.bilibili.com/room/v1/Room/get_info?room_id=' + \
            str(roomid)
        try:
            j = requests.get(url=url).json()
            if j:
                return int(j['data']['room_id']),int(j['data']['uid'])
            else: return roomid,0
        except Exception as e:
            ERROR(f'Request访问时发生异常：。异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            return roomid,0
    
    def Heartbeat(self):
        '''心跳'''
        try:
            self.ws.send(self.header_struct.pack(16, 16, 1,  2,  1))
        except Exception as e:
            ERROR(f'{str(self.roomid)}发送心跳异常：{e.__doc__}')

    def Onmessage(self,data,opcode,b):
        '''收到消息'''
        if not data:
            return
        data_l = 0
        len_datas = len(data)
        while data_l != len_datas:
            tuple_header = self.header_struct.unpack_from(data[data_l:])
            len_data, len_header, ver, opt, _ = tuple_header
            body_l = data_l + len_header
            next_data_l = data_l + len_data
            body = data[body_l:next_data_l]
            #数据包类型：2客户端心跳，3服务端心跳，5实际消息通知，7客户端加入房间，8服务器认证成功；偏移8，长度4
            if ver == 2:
                self.Onmessage(zlib.decompress(body),opcode,b)
            else:
                if opt == 3:
                    pass
                elif opt == 5:
                    j = json.loads(body.decode('utf-8'))
                    self.func.get(j['cmd'],self.Onother)(j)
                elif opt == 8:
                    print(f'{self.roomid}进入房间。')
                    #将心跳任务加入调度器并立即执行
                    if not self.job:
                        self.job = scheduler.add_job(self.Heartbeat, 'interval', seconds=30, next_run_time=datetime.datetime.now())
                    else:
                        #重新启动心跳任务
                        self.job.resume()
                    #Thread(target = self.Heartbeat,name = f'{self.roomid}').start()
            data_l = next_data_l

    def Onopen(self):
        '''ws已连接'''
        '''发送进入直播间信息'''
        INFO(f'{str(self.roomid)}ws连接成功,发送进入房间信息。')
        str_enter = f'{{"uid":0,"roomid":{str(self.roomid)},"protover":1,"platform":"web","clientver":"1.5.13"}}'
        body = str_enter.encode('utf-8')
        #合成头部                         总长度          头  ver opt sep
        header = self.header_struct.pack(len(body) + 16, 16, 1,  7,  1)
        self.ws.send(header + body)

    def Onclose(self):
        '''ws断开'''
        INFO(f'{str(self.roomid)}ws断开，暂停心跳任务！')
        if self.job:
            #暂停心跳任务
            self.job.pause()

    def run_forever(self,wsurl='wss://broadcastlv.chat.bilibili.com:443/sub'):
        '''运行弹幕连接并处理'''
        self.ws = websocket.WebSocketApp(wsurl,on_open=self.Onopen,on_close=self.Onclose,on_data=self.Onmessage)
        while self.ws.run_forever():
            INFO(f'{self.roomid} websocket断开连接，等待60秒后重新连接。')
            time.sleep(60)
        #停止心跳
        if self.job:
            self.job.remove()

if __name__ == '__main__':
    a = Danmu(2458117,'onlynull')
    b = Danmu(218,'onlynull')
    Thread(target = b.run_forever).start()
    a.run_forever()