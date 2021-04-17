# -*- coding: utf-8 -*-
from .Acfun import Acfun
from msgType import MsgChain
from Log import ERROR, INFO
import os
import yaml
import time

__all__ = (
    'Main',             #此方法不可以注释，否则本模块将不会被添加进任务
    #'on_GroupMessage',  #不需要接收群消息时将此行注释既可
    #'on_FriendMessage'  #不需要接收私聊消息时将此行注释既可
    )

#发送消息的函数
Send = {'sendGroupMsg': None, 'SendFriendMsg': None}
#配置文件路径
path = os.path.dirname(os.path.realpath(__file__)) + '\\config.yml'

def SendGroupsMsg(Groups,Msg:MsgChain):
    for Group in Groups:
        Send['sendGroupMsg'](Group,Msg)

def run():
    #读取配置文件
    try:
        file = open(path,  mode='r', encoding='utf-8')
        #转化yml配置数据
        data = yaml.load(file, Loader=yaml.FullLoader)
        file.close()
        #print(data)
    except Exception as e:
        ERROR(f'读入配置文件时发生异常，无法继续运行Acfun模块。异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
        return
    #实例化所有需要监听的对象放进列表里
    user = []
    for u in data['user']:
        INFO('初始化用户：'+u['uid'])
        us = Acfun(u)
        user.append(us)
    #开始循环执行
    while True:
        i = 0
        l = len(user)
        while i < l:
            try:#获取信息
                user[i].Getinfo()
                user[i].GetDynamic()
                #判断
                if user[i].IsNewLive():#开播
                    INFO(f'主播{user[i].Name}开播了~')
                    SendGroupsMsg(user[i].user['group'],user[i].LiveLoad())
                if user[i].IsNewVideo():#有新视频
                    INFO(f'主播{user[i].Name}有新视频了~')
                    SendGroupsMsg(user[i].user['group'],user[i].VideoLoad())
                if user[i].IsNewDynamic():#有新动态
                    INFO(f'主播{user[i].Name}有新动态了~')
                    SendGroupsMsg(user[i].user['group'],user[i].DynamincLoad())
                pass
            except Exception as e:
                ERROR(f'处理时发现异常，跳过！。异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
                pass
            i = i + 1
            time.sleep(data.get('delay',5))
        time.sleep(2)

def Main(sendGroupMsg, SendFriendMsg):
    #传递回调函数
    Send['sendGroupMsg']=sendGroupMsg
    run()
