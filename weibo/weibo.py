from logging import error
from msgType import *
from .weiboload import Weibo
from Log import INFO,ERROR,WARN
from .setting import groupid, getName, groupAt
import time
import random
import json
import os

__all__ = (
    'Main',
    #'on_GroupMessage',
    #'on_FriendMessage'
    )

Send={'sendGroupMsg':None,'SendFriendMsg':None}

weibo_id_array = {}
firstcheck_weibo = True

def getWeibo(index):
    idoleName = getName(index)
    weibo = Weibo(index)
    groups = groupid(index)
    at = str(groupAt(index))
    try:
        #INFO('check weibo')
        global weibo_id_array
        # 初次启动记录前十条微博id
        if firstcheck_weibo is True:
            INFO('first check weibo')
            weibo_id_array[index] = weibo.IdArray  # ******
            INFO(weibo_id_array[index])
        if firstcheck_weibo is False:
            # 取最新的前三条微博
            for idcount in range(0, 3):
                # 广告位微博id为0，忽略
                if int(weibo.IdArray[idcount]) == 0:
                    continue
                # 微博id不在记录的id列表里，判断为新微博
                if weibo.IdArray[idcount] not in weibo_id_array[index]:
                    msg = MsgChain()
                    if groupAt(index):
                        msg.joinAT(-1)
                    # 将id计入id列表
                    weibo_id_array[index].append(weibo.IdArray[idcount])
                    # 检查新微博是否是转发
                    if weibo.checkRetweet(idcount):
                        msg.joinPlain('%s 刚刚转发了一条微博：\n' % idoleName)
                        msg.joinPlain('%s\n' % weibo.getRetweetWeibo(idcount))
                    # 原创微博
                    else:
                        msg.joinPlain('%s 刚刚发了一条新微博：\n' % idoleName)
                        msg.joinPlain('%s\n' % weibo.getWeibo(idcount))
                        # 检查原创微博是否带图
                        if weibo.checkPic(idcount):
                            # 只取第一张图，pro可以直接发图，air则无
                            for pic in weibo.getPic(idcount):
                                msg.joinImg(Url=pic)
                    # msg.append(
                    #     {
                    #         'type': 'text',
                    #         'data': {'text': '\n传送门：%s\n' % weibo.getScheme(idcount)}})
                    for grpid in groups:
                        Send['sendGroupMsg'](grpid,msg)
                        time.sleep(0.5)
                    # print(msg)
    except Exception as e:
        WARN('error when getWeibo:' + str(e))
    finally:
        pass
        #INFO('weibo check completed')

def chaWeribo(data):
    global firstcheck_weibo
    random.shuffle(data['weibo'])
    idoles = data['weibo']
    for i, item in enumerate(idoles):
        #INFO(item['name'])
        getWeibo(i)
        time.sleep(1)
    if firstcheck_weibo is True:
        firstcheck_weibo = False

def Main(sendGroupMsg,SendFriendMsg):
    Send['sendGroupMsg']=sendGroupMsg
    Send['SendFriendMsg']=SendFriendMsg
    INFO('微博启动')
    # 打开json文件
    try:
        fb = open(os.path.dirname(os.path.realpath(__file__)) + '\ini.json', 'rb')
        data = json.load(fb)
        fb.close()
    except:
        ERROR('读入配置文件或解析时发生异常，检查配置文件是否正确，默认路径为.BILI目录下的ini.json。如果没有则需要复制文件 _ini(将我复制改名为ini.json).json 为 ini.json')
        return
    while True:
        chaWeribo(data)
        time.sleep(20)

def on_GroupMessage(Message:MsgChain,sender:GroupInfo):
    print('weibo收到群消息',Message.GetCQ())

def on_FriendMessage(Message:MsgChain,sender:SenderInfo):
    print('weibo收私聊消息',Message.GetCQ())