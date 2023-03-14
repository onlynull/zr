from msgType import *
from Log import ERROR
#from Log import INFO, ERROR
import os
import re
import requests
import time
import random

屏蔽群列表=[]


__all__ = (
    'Main',  # 此方法不可以注释，否则本模块将不会被添加进任务
    'on_GroupMessage',  # 不需要接收群消息时将此行注释既可
    #'on_FriendMessage'  # 不需要接收私聊消息时将此行注释既可
)
#发送消息的函数
Send = {'sendGroupMsg': None, 'SendFriendMsg': None}
#当前模块所在的目录
path = os.path.dirname(os.path.realpath(__file__)) + '\\Image'

def getdirs(file_dir):
    '''取指定目录下的文件夹列表，不对文件夹再取子目录'''
    for root, dirs, files in os.walk(file_dir):
        return dirs

def getfile(file):
    for root, dirs, files in os.walk(file):
        return files

def on_GroupMessage(Message: MsgChain, sender: GroupInfo):
    if sender.GroupId in 屏蔽群列表:
        return None
    s = Message.GetCQ()
    if s == 'ls':
        #发送列表
        a = getdirs(path+'\\'+str(sender.GroupId))
        if a and len(a) >= 1:
            Send['sendGroupMsg'](sender.GroupId,MsgChain().joinPlain(', '.join(a)))
    elif s.startswith('/'):
        #符合初步判断
        if s.find('[CQ:image') != -1:
            try:
                #存在图片，表示要添加，正则取出图片
                #由于CQ和mirai取出的cq码格式不一样，先匹配url格式的
                urlpattern='/(.*?)\[CQ:image,file=.*,url=(.*)\]'
                filepattern='/(.*?)\[CQ:image,file=(.*)\]'
                r = re.search(urlpattern,s)
                if r:
                    Imgurl = r.group(2)
                    dn = r.group(1)
                else:
                    r = re.search(filepattern,s)
                    if r:
                        Imgurl = r.group(2)
                        dn = r.group(1)
                        if dn == '汪姐姐':
                            Send['sendGroupMsg'](sender.GroupId,MsgChain().joinPlain('guna~ 哼！'))
                            return
                    else:
                        Imgurl = None
                        dn = None
                if Imgurl:
                    #取出图片url，保存图片
                    r = requests.get(Imgurl).content
                    fd = path+'\\'+str(sender.GroupId)+'\\'+ dn.replace(' ','').replace('\r','')
                    #检查此群目录是否存在
                    if os.path.isdir(fd) == False:
                        os.makedirs(fd)
                    with open(fd +'\\'+str(time.time()*1000)+'.jpg','wb') as f:
                        f.write(r)
                        Send['sendGroupMsg'](sender.GroupId,MsgChain().joinPlain('加好啦~'))
            except Exception as e:
                ERROR(f'添加图片异常，异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
                Send['sendGroupMsg'](sender.GroupId,MsgChain().joinPlain('添加失败！'))
        else:
            #看看存不存在图片，存在就发
            try:
                fd = path+'\\'+str(sender.GroupId)+'\\'+ s.replace('/','\\')
                fl = getfile(fd)
                if fl and len(fl) >= 1:
                    f = fl[random.randint(0,len(fl)-1)]
                    #print(f)
                    msg = MsgChain()
                    msg.joinImg(fd+'\\'+f)
                    Send['sendGroupMsg'](sender.GroupId,msg)
            except Exception as e:
                ERROR(f'发送图片异常，异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')

def Main(sendGroupMsg, SendFriendMsg):
    #传递回调函数
    Send['sendGroupMsg']=sendGroupMsg
