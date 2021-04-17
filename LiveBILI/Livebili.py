from time import time
from Log import INFO,ERROR
from .danmu import Danmu
from threading import Thread
from msgType import MsgChain
import os,json,time,sqlite3,requests

__all__ = (
    'Main',             #此方法不可以注释，否则本模块将不会被添加进任务
    #'on_GroupMessage',  #不需要接收群消息时将此行注释既可
    #'on_FriendMessage'  #不需要接收私聊消息时将此行注释既可
    )

#用来存放发送消息回调，也可以通过其他方法保存
Send={'sendGroupMsg':None,'SendFriendMsg':None}

#配置文件路径
Configpath = os.path.dirname(os.path.realpath(__file__))

#创建data文件夹
if os.path.isdir(Configpath+'\\data') == False:
    os.makedirs(Configpath+'\\data')

class SQL():
    gift = '''CREATE TABLE GIFT(
       TIME           TEXT,
       UNAME          TEXT,
       UID            INTEGER,
       GIFTNAME       TEXT,
       GIFTNUM        INT,
       PRICE          INTEGER,
       GIFTCOIN       TEXT);'''
    
    danmu = '''CREATE TABLE DANMU(
       TIME           TEXT,
       UNAME          TEXT,
       UID            INTEGER,
       MSG            TEXT);'''

    guard = '''CREATE TABLE GUARD(
       TIME           TEXT,
       UNAME          TEXT,
       UID            INTEGER,
       GUARDTYPE      TEXT,
       NUM            INT,
       PRICE          INTEGER);'''

    def __init__(self,info:dict):
        self.info = info
        if info.get('savegift') or info.get('savedanmu'):
            #check_same_thread = False,这里要提交这个参数，否则会导致无法在线程操作sql
            self.sql3 = sqlite3.connect(Configpath + f'\\data\\{self.info["roomid"]}.db',check_same_thread = False)
            self.sql = self.sql3.cursor()
            #首次打开就建表，如果存在直接try
            if info['savegift']:
                try:
                    self.sql.execute(self.gift)
                    self.sql3.commit()
                except Exception as e:
                    pass
                    #INFO('数据库表已存在')
            if info['savedanmu']:
                try:
                    self.sql.execute(self.danmu)
                    self.sql3.commit()
                except Exception as e:
                    pass
                try:
                    self.sql.execute(self.guard)
                    self.sql3.commit()
                except Exception as e:
                    pass
        else:
            self.sql = None

    def __del__(self):
        self.sql3.close()

    def savegift(self,
        TIME,
        UNAME,
        UID,
        GIFTNAME,
        GIFTNUM,
        PRICE,
        GIFTCOIN):
        '''保存礼物日志'''
        t = f"INSERT INTO GIFT VALUES ('{TIME}', '{UNAME}', {UID}, '{GIFTNAME}', {GIFTNUM}, {PRICE}, '{GIFTCOIN}' )"
        #print(t)
        try:
            self.sql.execute(t)
            self.sql3.commit()
        except Exception as e:
            ERROR(f'保存礼物日志发生异常：异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')

    def savedanmu(self,
        TIME,
        UNAME,
        UID,
        MSG):
        '''保存弹幕'''
        t = f"INSERT INTO DANMU VALUES ('{TIME}', '{UNAME}', {UID}, '{MSG}' )"
        
        #print(t)
        try:
            self.sql.execute(t)
            self.sql3.commit()
        except Exception as e:
            ERROR(f'保存弹幕信息发生异常：异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')

    def saveguard(self,
        TIME,
        UNAME,
        UID,
        GUARDTYPE,
        NUM,
        PRICE):
        '''保存舰队信息'''
        t = f"INSERT INTO GUARD VALUES ('{TIME}', '{UNAME}', {UID}, '{GUARDTYPE}', {NUM}, {PRICE} )"
        self.sql.execute(t)
        self.sql3.commit()


class Livebiliws(Danmu):
    def __init__(self,info:dict) -> None:
        self.info = info
        super().__init__(int(info['roomid']))
        self.status = False
        self.title = None
        self.area = None
        self.VOICE_name = None
        self.giftsql = None
        self.danmusql = None
        self.SQL = SQL(self.info)

    def OnDANMU_MSG(self,data):
        '''收到弹幕消息'''
        #print(f'[{str(self.roomid)}]{data["info"][2][1]}：{data["info"][1]}')
        if self.info.get('savedanmu'):
            self.SQL.savedanmu(
                data["info"][0][4],#时间
                data["info"][2][1],#用户名
                data['info'][2][0],#用户uid
                data['info'][1]    #弹幕
            )

    def OnLIVE(self,data):
        '''开播调用'''
        INFO(f'{self.roomid}[{self.info.get("showname",self.info.get("name"))}]收到开播推送')
        if not self.status:
            for group in self.info['Group']:
                msg = MsgChain()
                if group['ATall']:
                    msg.joinAT(-1)
                msg.joinPlain(f'你的小可爱{self.info.get("showname",self.info.get("name"))}开播啦~')
                if self.title:
                    msg.joinPlain(f'\n【{self.title}】')
                if group['sendPic']:
                    ''''''
                if group['sendUrl']:
                    msg.joinPlain(f'\nhttps://live.bilibili.com/{self.roomid}')
                Send['sendGroupMsg'](group['id'],msg)
                time.sleep(0.2)
        self.status = True
        #保存开播日志在弹幕表中
        if self.info.get('savedanmu'):
            self.SQL.savedanmu(
                time.time()*1000,#时间
                'null',#用户名
                'null',#用户uid
                'LIVE'    #弹幕
            )

    def OnPREPARING(self,data):
        '''下播调用'''
        INFO(f'{self.roomid}[{self.info.get("showname",self.info.get("name"))}]收到下播推送')
        #self.SendMSG(f'你的小可爱{self.info.get("showname","None")}开播啦~\nhttps://live.bilibili.com/{self.roomid}')
        self.status = False
        self.SendMSG(MsgChain().joinPlain(f'你的小可爱{self.info.get("showname",self.info.get("name"))}下播啦~'))
        #保存下播日志在弹幕表中
        if self.info.get('savedanmu'):
            self.SQL.savedanmu(
                time.time()*1000,#时间
                'null',#用户名
                'null',#用户uid
                'PREPARING'    #弹幕
            )

    def OnGIFT(self,data):
        '''收到礼物'''
        gift_uname=data['data']['uname']
        gift_num=data['data']['num']
        gift_giftname=data['data']['giftName']
        gift_price=data['data']['price']
        gift_coin_type=data['data']['coin_type']
        if int(gift_price) >= 80000 and gift_coin_type == 'gold': #默认屏蔽80元以下的礼物和默认屏蔽银瓜子
            self.SendMSG(MsgChain().joinPlain(f'你的小可爱{self.info.get("showname",self.info.get("name"))}收到礼物：{gift_giftname}*{gift_num} From {gift_uname}'))
        #保存礼物日志
        if self.info.get('savegift'):
            d = data['data']
            self.SQL.savegift(
                d['timestamp'],
                d['uname'],
                d['uid'],
                d['giftName'],
                d['num'],
                d['price'],
                d['coin_type'])

    def OnCHANGE(self,data):
        '''房间信息：修改标题，修改分区'''
        self.title = data['data']['title']
        self.area = f'{data["data"]["area_name"]}·{data["data"]["parent_area_name"]}'
        INFO(f'{self.roomid}修改分区或标题 【{self.title}】 {self.area}')
        self.SendMSG(MsgChain().joinPlain(f'{self.title}\n{self.area}'))

    def OnCUT_OFF(self,data):
        '''房间被切'''
        self.SendMSG(MsgChain().joinPlain(f'{data}'))
        #保存房间被切日志在弹幕表中
        if self.info.get('savedanmu'):
            self.SQL.savedanmu(
                time.time()*1000,#时间
                'null',#用户名
                'null',#用户uid
                str(data)    #弹幕
            )

    def OnANCHOR_LOT_START(self,data):
        '''天选时刻抽奖开始'''
        msg = MsgChain()
        msg.joinPlain(f'天选时刻抽奖开始 [{data["data"]["id"]}]\n奖品：{data["data"]["award_name"]}*{data["data"]["award_num"]}')
        if data['data'].get('danmu'):
            msg.joinPlain(f'\n弹幕：{data["data"].get("danmu")}')
        if data['data'].get('gift_name'):
            msg.joinPlain(f'\n赠送礼物：{data["data"].get("gift_name")}')
        if data['data'].get('require_text'):
            msg.joinPlain(f'\n抽奖限制：{data["data"].get("require_text")}')
        if data['data'].get('award_image'):
            msg.joinImg(Url=data['data'].get('award_image'))
        self.SendMSG(msg)

    def OnANCHOR_LOT_AWARD(self,data):
        '''天选时刻中间信息'''
        msg = MsgChain()
        msg.joinPlain(f'天选时刻中奖信息 [{data["data"]["id"]}]\n中奖用户：')
        users=[].copy()
        for user in data['data']['award_users']:
            users.append(user['uname']+'['+user['uid']+']')
        msg.joinPlain('、'.join(users)+f'\n中奖奖品：{data["data"]["award_name"]}')
        self.SendMSG(msg)

    def OnVOICE_JOIN_STATUS(self,data):
        '''连麦'''
        #因为未知bug，会重复推送
        if self.VOICE_name != data['data']['user_name']:
            self.VOICE_name = data['data']['user_name']
            self.SendMSG(MsgChain().joinPlain(f'直播间连麦，当前语音接入：{self.VOICE_name}'))

    def OnGUARD_BUY(self,data):
        '''舰队'''
        self.SendMSG(MsgChain().joinPlain(f'{self.info.get("showname",self.info.get("name"))}的舰队消息：{data["data"]["username"]}在本房间开通了{data["data"]["gift_name"]}*{data["data"]["num"]}'))
        #保存舰队日志
        if self.info.get('savegift'):
            d = data['data']
            self.SQL.saveguard(
                d.get('timestamp',time.time()*1000),
                d['username'],
                d['uid'],
                d['gift_name'],
                d['num'],
                d['price'])

    def OnWARNING(self,data):
        '''收到警告'''
        self.SendMSG(MsgChain().joinPlain(f'{self.roomid}收到警告\n{data}'))
        #保存房间被警告日志在弹幕表中
        if self.info.get('savedanmu'):
            self.SQL.savedanmu(
                time.time()*1000,#时间
                'null',#用户名
                'null',#用户uid
                str(data)    #弹幕
            )

    def Onother(self,data):
        '''其他消息'''
        #print(data)
    
    def OnINTERACT_WORD(self,data):
        '''用户进入直播间'''
        #保存用户进入房间日志在弹幕表中
        if self.info.get('savedanmu') and data['data']['msg_type'] == 1:
            self.SQL.savedanmu(
                data['data']['timestamp'],#时间
                data['data']['uname'],#用户名
                data['data']['uid'],#用户uid
                'INTERACT_WORD'    #弹幕
            )

    def SendMSG(self,msg:MsgChain):
        #发送直播间消息至群
        for group in self.info['Group']:
            if group.get('roominfo'):
                Send['sendGroupMsg'](group['id'],msg)

    def RefreshInfo(self):
        '''刷新用户部分信息'''
        try:
            j = requests.get(url='https://api.live.bilibili.com/room/v1/Room/get_info?room_id='+str(self.roomid)).json()
            if j :
                self.uid = j['data']['uid']
                self.title = j['data']['title']
                self.area = j['data']['area_name']
                j = requests.get(url='https://api.live.bilibili.com/live_user/v1/Master/info?uid='+str(self.uid)).json()
                if j :
                    self.info['name'] = j['data']['info']['uname']
        except Exception as e:
            ERROR(f'刷新用户信息时发生异常：异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')

def run_task():
    # 读入配置文件
            INFO('读入配置文件...')
            try:
                file = open(Configpath + '\config.json', mode='r', encoding='utf-8')
                config = json.load(file)
                file.close()
            except:
                ERROR('读入配置文件或解析时发生异常，检查配置文件是否正确，默认路径为.LIVEBILI目录下的config.json。如果没有则需要复制文件 _config(将我复制改名为config.json).json 为 config.json 如果你已经配置好了BILI的配置文件也可将其直接复制过来使用（必须要填写roomid）')
                return
            INFO('开始初始化所有需要监听的用户')
            user = []
            user.clear()
            for u in config['config']:
                if u.get('roomid'):
                    user.append(Livebiliws(u))
                else:
                    ERROR(f'{u}未填写roomid')
            if len(user) == 0:
                INFO('没有载入任何需要监听的用户')
                return
            INFO('开始启动ws')
            i = 0
            for u in user:
                Thread(target = u.run_forever,name=f'[T{i}] {u.roomid}-websocket').start()
                i += 1
            #开始刷新用户信息，间隔5秒
            for u in user:
                u.RefreshInfo()
                time.sleep(5)

def Main(sendGroupMsg,SendFriendMsg):
    '''启动程序，并传入消息发送的回调函数'''
    #保存回调函数
    Send['sendGroupMsg']=sendGroupMsg
    Send['SendFriendMsg']=SendFriendMsg
    run_task()

if __name__ == "__main__":
    a = {
      "uid": "15272008",
      "roomid": 2458117,
      "name": "",
      "showname": "/bin/cat",
      "savegift":True,
      "savedanmu":True,
      "Group": [
        {
          "id": 691963133,
          "ATall": False,
          "sendPic": True,
          "sendUrl": True,
          "roominfo": True
        }
      ]
    }
    Livebiliws(a).run_forever()    