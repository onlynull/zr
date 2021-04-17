# -*- coding: utf-8 -*-
from json.decoder import JSONDecoder
from logging import error
import time
import requests
import json
from requests import sessions
import websocket
import threading
from msgType import *
from Log import INFO,ERROR,DEBUG

GroupMessagefunc = []
FriendMessagefunc = []
def on_GroupMessage(func):
    GroupMessagefunc.append(func)

def on_FriendMessage(func):
    FriendMessagefunc.append(func)

class on_msg(threading.Thread):
    def __init__(self, msg, mode) -> None:
        threading.Thread.__init__(self)
        self.mode = mode
        self.msg = json.loads(msg)

    def run(self):

        # 新建线程的方式处理
        # 分析消息来源是cqhttp还是miraihttp
        msg = MsgChain()
        #print(self.msg)
        if self.mode == 'mirai_api_http':
            t = self.msg.get('type')
            if t == 'FriendMessage' or t == 'GroupMessage':
                sender = msg.AddMraiMsg(self.msg)
            else:return
        else:
            #预处理
            if self.msg.get('post_type') == 'message':
                sender = msg.AddCQMsg(self.msg)
            else:return
        # 开始分发消息
        if msg.fromType == 'Group':
            print(f'{time.strftime("[%Y-%m-%d %H:%M:%S]",time.localtime())} 群消息[{str(sender.GroupId)}] -> {sender.Sendername}：{msg.GetCQ()}')
            for f in GroupMessagefunc:
                f(Message=msg,sender=sender)
        elif msg.fromType == 'Friend':
            print(f'{time.strftime("[%Y-%m-%d %H:%M:%S]",time.localtime())} 私聊消息[{str(sender.Senderid)}] -> {sender.Sendername}：{msg.GetCQ()}')
            for f in FriendMessagefunc:
                f(Message=msg,sender=sender)

class websock():
    def __init__(self,url) -> None:
        self.ws = websocket.WebSocketApp(url,on_message=self.on_message,on_close=self.on_close,on_open=self.on_open)
    
    def on_message(self, message):
        '''收到ws消息，并启动线程去处理他'''
        DEBUG('ws收到消息：' + message)
        m = on_msg(message,self.mode)
        m.start()

    def on_close(self):
        ERROR('ws关闭，断开连接')
    
    def on_open(self):
        INFO(self.mode + '_websocket连接成功')

class mirai(websock):
    '''自制简易miraihttp通信模块'''
    mode = 'mirai_api_http'
    authkey = ""
    host = ""
    sessionstr = ""
    def __init__(self, authkey='LoveZR', BOTQQ=123456789, HOST='http://127.0.0.1:8888/'):
        QQBOT = 'mirai'
        if HOST[-1] == "/":
            self.host = HOST
        else:
            self.host = HOST + "/"
        self.BOTQQ = BOTQQ
        self.authkey = authkey
        if not self.__Getsessionstr__():
            raise Exception('mirai_api_http初始化失败，检查网络和ip、authkey、botqq')
        '''至此初始化完成'''

    def __Getsessionstr__(self):
        '''获取sessionstr'''
        data = {'authKey': self.authkey}
        r = self.POST('auth', json.dumps(data))
        if r['code'] == 0:
            self.sessionstr = r['session']
            INFO(f'session：{self.sessionstr}')
        else:
            #err = '错误的MIRAI API HTTP auth key'
            ERROR(r['msg'])
            return False
        
        '''获取到session，绑定机器人'''
        data = {'sessionKey': self.sessionstr, 'qq': int(self.BOTQQ)}
        r = self.POST('verify', json.dumps(data))
        if r['code'] == 0:
            INFO("绑定机器人成功")
            super().__init__(self.host.replace('http','ws')+'all?sessionKey='+self.sessionstr)
        else:
            err = r['msg']
            ERROR(err)
            return False
        return True

    def GET(self, path, data):
        '''为内部访问使用方法'''
        if data == '':
            d = ''
        else:
            d = '?' + data
        url = f"{self.host}{path}{d}"
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 \
            Safari/537.36'}
        try:
            return requests.get(url, headers=header).json()
        except Exception as e:
            ERROR(f'mirai在http_get时发生错误：url：{url} data:{str(data)}；异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            return {'code':-1,'msg':'request.get 发生异常，请检查网络！'}

    def POST(self, path, data):
        '''为内部访问使用方法'''
        url = f"{self.host}{path}"
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 \
            Safari/537.36',
            'content-type': 'application/json'}
        try:
            if type(data) == dict:
                data = json.dumps(data)
            print(data)
            r = requests.post(url, data, headers=header)
            print(r.text)
            return r.json()
        except Exception as e:
            ERROR(f'mirai在http_post时发生错误：url：{url} data:{str(data)}；异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            return {'code':-1,'msg':'request.post 发生异常，请检查网络！'}

    def uploadImage(self,p,type='group'):
        '''提交文件路径,上传完成后返回url，失败返回None'''
        body = {
            'img':('1.jpg',open(p,'rb'),'image/jpeg'),
            'sessionKey':(None,self.sessionstr),
            'type':(None,type)
            }
        url = self.host+'uploadImage'
        j = requests.post(url,files=body).json()
        #print(j)
        return j

    def uploadVoice(self,p,type='group'):
        '''提交文件路径,上传完成后返回url，失败返回None'''
        body = {
            'voice':('1.mp3',open(p,'rb'),'voice/mp3'),
            'sessionKey':(None,self.sessionstr),
            'type':(None,type)
            }
        url = self.host+'uploadVoice'
        j = requests.post(url,files=body).json()
        #print(j)
        return j

    def Send(self,target:int,Msg: MsgChain,m = 'sendGroupMessage'):
        '''发送一条消息(可以为指定发送群消息还是私聊消息)，消息为消息链类型,封装的类型'''
        try:
            #语音文件单独处理，后期可能会修改
            if len(Msg.msg) == 1 and Msg.msg[0]['type'] == 'Voice':
                #因为语音只能单独发送
                if Msg.msg[0]['url'] and not Msg.msg[0]['voiceId']:
                    #进行上传并赋值
                    fname=f'./data/{str(time.time()*1000)}.mp3'
                    with open( fname,'wb' ) as f:
                        f.write(requests.get(Msg.msg[0]['url']).content)
                    Msg.msg[0]['voiceId'] = self.uploadVoice(fname)['voiceId']
        except:
            pass
        INFO(f'发送{"群" if m == "sendGroupMessage" else "私聊"}消息[{str(target)}] <- {Msg.GetCQ()}')
        s = {'sessionKey': self.sessionstr, 'target': 
            target,'quote':Msg.Quote, 'messageChain': Msg.msg}
        ss = json.dumps(s)
        j = self.POST(m, ss)
        INFO(str(j))
        if j.get('code') == 6:
            #指定文件不存在，出现于发送本地图片
            #表示我发送的图片路径对于机器人而言并找不到，直接读取发送文件
            try:
                mesg = MsgChain()
                for msg in Msg.msg:
                    if msg['type'] == 'Image':
                        p = msg['path']
                        img = self.uploadImage(p,'group' if m == 'sendGroupMessage' else 'friend')
                        if img:
                            mesg.joinImg(ImageId=img['imageId'],
                            #Url=img['url']
                            )
                    else:   #来点魔法，但这样使用会导致下一步发送消息时日志输出缺失
                        mesg.msg.append(msg.copy())
                return self.Send(target,mesg,m)
            except Exception as e:
                ERROR(f'mirai在上传图片时发生错误：异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
        else: return j

    def SendGroupMsg(self, GroupId, Msg: MsgChain):
        '''发送一条群消息，消息为消息链类型'''
        return self.Send(int(GroupId),Msg,'sendGroupMessage')

    def SendFriendMsg(self,FriendId,Msg: MsgChain):
        '''发送一条私聊消息，消息为消息链类型'''
        return self.Send(int(FriendId),Msg,'sendFriendMessage')

    def run_forever(self):
        '''阻塞运行连接ws，并接受消息'''
        try:
            #检查sessionstr是否可用
            j = self.GET('config','sessionKey='+self.sessionstr)
            if j.get('sessionKey') == self.sessionstr:
                pass
            elif j.get('code') == 3:
                #sessionstr失效
                INFO(f'{j["msg"]}，重新获取')
                self.__Getsessionstr__()
            else:
                ERROR(j['msg'])
                return True
            return self.ws.run_forever(ping_interval=30,ping_timeout=3)
        except:
            ERROR(f'mirai_api_http在ws连接时发生异常。')
            return True

    def mute(self, Group, QQID, time):
        '''
        设置禁言
        QQID > 0 时为群成员禁言设置，否则为全体禁言设置
        time > 0 时为禁言时长(全体禁言直接填1既可)，否则为解除禁言
        '''
        INFO(f'设置禁言：Gropu:{Group},QQ:{QQID},TIME:{time}')
        s = {'sessionKey': self.sessionstr, 'target': Group,}
        if QQID > 0:
            #禁言或者解除群员禁言
            if time > 0:
                path = 'mute'
                s['memberId'] = QQID
                s['time'] = time
            else:
                path = 'unmute'
                s['memberId'] = QQID
        else:
            #全体禁言或解除
            if time > 0:
                path = 'muteAll'
            else:
                path = 'unmuteAll'
        print(self.POST(path,s))

    def groupConfig(self,Group,config:dict=None):
        '''按照下列格式传入dict，不修改不传入既可
        "config": 
        {
        "name": "群名称",
        "announcement": "群公告",
        "confessTalk": true,
        "allowMemberInvite": true,
        "autoApprove": true,
        "anonymousChat": true
        }
        '''
        if config:
            data = {
                "sessionKey": self.sessionstr,
                "target": Group,
                "config": config}
            return self.POST('groupConfig',data)
        else:
            return self.GET('groupConfig',f'sessionKey={self.sessionstr}&target={Group}')

    def groupList(self):
        return self.GET('groupList','sessionKey='+self.sessionstr)


class cq(websock):
    mode = 'cqhttp'
    def __init__(self,access_token='',host='127.0.0.1',http_port='5700',ws_port='6700') -> None:
        self.access_token=access_token
        self.host=f'http://{host}:{http_port}/'
        self.wshost=f'ws://{host}:{ws_port}/all?access_token={access_token}'
        j = self.GET('get_login_info',{'access_token':self.access_token})
        if j['retcode'] == 0:
            self.BOTQQ = j['data']['user_id']
        else:
            raise Exception(j.get('msg','cqhttp初始化时发生未知错误'))
        #初始化ws
        super().__init__(self.wshost)

    def GET(self,path,data):
        url = f'{self.host}{path}'
        try:
            r = requests.get(url, params=data)
            if r.status_code == 200:
                return r.json()
            else:
                return {'retcode':r.status_code,'msg':f'code:{r.status_code},code=401表示access_token错误'}
        except Exception as e:
            ERROR(f'cq在http_get时发生错误：url：{url} data:{str(data)}；异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            return {'retcode':-1,'msg':'request.get 发生异常'}

    def SendGroupMsg(self,GroupId, Msg: MsgChain):
        INFO(f'发送群消息[{str(GroupId)}] <- {Msg.GetCQ()}')
        if Msg.Quote:
            mes = '[CQ:reply,id=' + str(Msg.Quote) + ']' + Msg.GetCQ()
        else:
            mes = Msg.GetCQ()
        s = {
            'access_token':self.access_token,
            'group_id':GroupId,
            'message':mes
        }
        j = self.GET('send_group_msg',data=s)
        INFO(str(j))
        return j
    
    def SendFriendMsg(self,FriendId,Msg: MsgChain):
        INFO(f'发送私聊消息[{str(FriendId)}] <- {Msg.GetCQ()}')
        if Msg.Quote:
            mes = '[CQ:reply,id=' + str(Msg.Quote) + ']' + Msg.GetCQ()
        else:
            mes = Msg.GetCQ()
        s = {
            'access_token':self.access_token,
            'user_id':FriendId,
            'message':mes
        }
        j = self.GET('send_private_msg',data=s)
        INFO(str(j))
        return j

    def run_forever(self):
        '''阻塞运行连接ws，并接受消息'''
        return self.ws.run_forever(ping_interval=30,ping_timeout=3)

    def mute(self, Group, QQID, time):
        '''
        设置禁言
        QQID > 0 时为群成员禁言设置，否则为全体禁言设置
        time > 0 时为禁言时长(全体禁言直接填1既可)，否则为解除禁言
        '''
        s = {'access_token': self.access_token, 'group_id': Group,}
        if QQID > 0:
            #禁言或者解除群员禁言
            if time > 0:
                path = 'set_group_ban'
                s['user_id'] = QQID
                s['duration'] = time
            else:
                path = 'set_group_ban'
                s['user_id'] = QQID
                s['duration'] = 0
        else:
            #全体禁言或解除
            if time > 0:
                path = 'set_group_whole_ban'
                s['enable'] = True
            else:
                path = 'set_group_whole_ban'
                s['enable'] = False
        self.GET(path,s)

if __name__ == "__main__":
    input('你开错啦，要运行LoveZR.py。你个憨憨！')