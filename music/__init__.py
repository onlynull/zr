import requests
import time
import json
import re
from msgType import MsgChain,GroupInfo

'''
提供网易云点歌功能
'''


__all__ = (
    'Main',  # 此方法不可以注释，否则本模块将不会被添加进任务
    'on_GroupMessage',  # 不需要接收群消息时将此行注释既可
    #'on_FriendMessage'  # 不需要接收私聊消息时将此行注释既可
)
#发送消息的函数
Send = {'sendGroupMsg': None, 'SendFriendMsg': None}


class WangYiYun:
    '''网易云点歌返回json字符串'''
    def __init__(self) -> None:
        return
    def GetSongs(self,name:str):
        url='http://music.163.com/api/search/pc'
        data={'s':name,'offset':0, 'limit':1, 'type':1}
        print(data)
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'}
        #proxies={'http':'127.0.0.1:8888'}
        return requests.post(url=url, data=data, headers=header).json()
    
    def MusicParse(self,name):
        '''搜索歌曲并生成可发送的app消息(json文本)'''
        #'token':'84b25142c1a6ca12283fe53c14e9f271',
        #添加token的话会导致部分歌曲无法发送
        appjson = {'app':'com.tencent.structmsg','config':{'autosize':True,'ctime':0,'forward':True,'type':'normal'},'desc':'音乐','meta':{'music':{'action':'','android_pkg_name':'','app_type':1,'appid':100495085,'desc':'[desc]','jumpUrl':'https://y.music.163.com/m/song?id=[id]','musicUrl':'http://music.163.com/song/media/outer/url?id=[id]','preview':'[preview]','sourceMsgId':'0','source_icon':'','source_url':'','tag':'网易云音乐','title':'[title]'}},'prompt':'[prompt]','ver':'0.0.0.1','view':'music'}
        r = self.GetSongs(name)
        r = r['result']['songs'][0]
        ars = []
        for ar in r['artists']:
            ars.append(ar['name'])
            pass
        desc = '/'.join(ars)
        appjson['config']['ctime'] = int(time.time())
        appjson['meta']['music']['desc'] = desc
        appjson['meta']['music']['jumpUrl'] = 'https://y.music.163.com/m/song?id=' + str(r['id'])
        appjson['meta']['music']['musicUrl'] = 'http://music.163.com/song/media/outer/url?id=' + str(r['id'])
        appjson['meta']['music']['preview'] = r['album']['picUrl']
        appjson['meta']['music']['title'] = r['name']
        appjson['prompt'] = f'[分享]{r["name"]}'
        return json.dumps(appjson,ensure_ascii=False)

        
class QQ:
    '''QQ点歌返回json字符串'''
    def __init__(self) -> None:
        return
    def GetSongs(self,name:str):
        url = f'http://c.y.qq.com/soso/fcgi-bin/client_search_cp?qqmusic_ver=1298&remoteplace=txt.yqq.song&new_json=1&p=1n=1&w={name}&format=json'
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Referer': 'https://y.qq.com/portal/player.html'
            }
        return requests.get(url=url, headers=header).json()
    
    def GetSongUrl(self,mid):
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Referer': 'https://y.qq.com/portal/player.html'
            }
        data='{"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"358840384","songmid":["002sPvGb1kLrAr"],"songtype":[0],"uin":"1443481947","loginflag":1,"platform":"20"}},"comm":{"uin":"18585073516","format":"json","ct":24,"cv":0}}'
        url='http://u.y.qq.com/cgi-bin/musicu.fcg?format=json&data='+data.replace('[mid]',mid)
        return requests.get(url,headers=header).json()

    def GetSongPic(self,mid):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36',
            'Referer': 'https://y.qq.com/portal/player.html'
            }
        url=f'http://y.qq.com/n/yqq/song/{mid}.html'
        r = requests.get(url,headers=header).content.decode('utf-8')
        #print('返回内容',r)
        o = re.search('(y.gtimg.cn/music/photo_new/.*?)\?',r)
        if o :
            return o.group(1)
        else:
            return ''
        

    def MusicParse(self,name):
        '''搜索歌曲并生成可发送的app消息(json文本)'''
        #'token':'84b25142c1a6ca12283fe53c14e9f271',
        #添加token的话会导致部分歌曲无法发送
        #音乐app格式大致类似，appid更改就可以了
        #appid 100497308
        xml=R"<?xml version='1.0'encoding='UTF-8' standalone='yes' ?><msg serviceID="+'"2" templateID="1" action="web" brief="[prompt]" sourceMsgId="0" url="[jumpUrl]" flag="0" adverSign="0" multiMsgFlag="0"><item layout="2"><audio cover="[preview]" src="[musicUrl]" /><title>[title]</title><summary>[desc]</summary></item><source name="QQ音乐" icon="https://i.gtimg.cn/open/app_icon/01/07/98/56/1101079856_100_m.png" url="http://web.p.qq.com/qqmpmobile/aio/app.html?id=1101079856" action="app" a_actionData="com.tencent.qqmusic" i_actionData="tencent1101079856://" appid="1101079856" /></msg>'
        x=xml
        appjson = {
        'app':'com.tencent.structmsg',
        'config':{
                'autosize':True,
                'ctime':None,
                'forward':True,
                'token': '8ec248e9b11886bbbda540278b25b7d2',
                'type':'normal'
                },
        'desc':'音乐',
        'extra':{
                'app_type':1,
                'appid':100497308,
                'uin':1234567
                },
        'meta':{
                'music':{
                        'action':'',
                        'android_pkg_name':'',
                        'app_type':1,
                        'appid':100497308,
                        'desc':'',
                        'jumpUrl':'',
                        'musicUrl':'',
                        'preview':'',
                        'sourceMsgId':'0',
                        'source_icon':'',
                        'source_url':'',
                        'tag':'QQ音乐',
                        'title':''
                        }
                },
        'prompt':'',
        'ver':'0.0.0.1',
        'view':'music'}
        r = self.GetSongs(name)
        #print(r)
        r = r['data']['song']['list'][0]
        ars = []
        for ar in r['singer']:
            ars.append(ar['name'])
            pass
        desc = '/'.join(ars)
        appjson['config']['ctime'] = int(time.time())
        appjson['meta']['music']['desc'] = desc
        appjson['meta']['music']['jumpUrl'] = f'https://y.qq.com/n/yqq/song/{r["mid"]}.html'+'?hosteuin=&sharefrom=gedan&from_id=7382629476&from_idtype=10014&from_name=JUU3JUIyJUJFJUU5JTgwJTg5JTIwJTdDJTIwJUU1JUE1JUJEJUU1JTkwJUFDJUU1JTg4JUIwJUU1JThEJTk1JUU2JTlCJUIyJUU1JUJFJUFBJUU3JThFJUFGJUU3JTlBJTg0JUU3JTgzJUFEJUU2JUFEJThD&songid=247261229&songmid=&type=0&platform=1&appsongtype=1&_wv=1&source=qq&appshare=iphone&media_mid=001PLl3C4gPSCI&ADTAG=qfshare'
        appjson['meta']['music']['title'] = r['name']
        appjson['prompt'] = f'[分享]{r["name"]}'
        j = self.GetSongUrl(r['mid'])
        #print(j)
        #appjson['meta']['music']['musicUrl'] = j['req_0']['data']['sip'][0]+j['req_0']['data']['midurlinfo'][0]['purl']
        appjson['meta']['music']['preview'] = 'http://'+self.GetSongPic(r['mid'])

        x = x.replace('[prompt]',f'[分享]{r["name"]}')
        x = x.replace('[jumpUrl]',f'https://y.qq.com/n/yqq/song/{r["mid"]}.html'+'?hosteuin=&sharefrom=gedan&from_id=7382629476&from_idtype=10014&from_name=JUU3JUIyJUJFJUU5JTgwJTg5JTIwJTdDJTIwJUU1JUE1JUJEJUU1JTkwJUFDJUU1JTg4JUIwJUU1JThEJTk1JUU2JTlCJUIyJUU1JUJFJUFBJUU3JThFJUFGJUU3JTlBJTg0JUU3JTgzJUFEJUU2JUFEJThD&songid=247261229&songmid=&type=0&platform=1&appsongtype=1&_wv=1&source=qq&appshare=iphone&media_mid=001PLl3C4gPSCI&ADTAG=qfshare')
        x = x.replace('[preview]','http://'+self.GetSongPic(r['mid']))
        #x = x.replace('[musicUrl]',j['req_0']['data']['sip'][0]+j['req_0']['data']['midurlinfo'][0]['purl'])
        x = x.replace('[musicUrl]','')
        x = x.replace('[title]',r['name'])
        x = x.replace('[desc]',desc)
        print(appjson)
        print(x)
        return x,json.dumps(appjson,ensure_ascii=False)

QQ点歌 = QQ()
网易云点歌 = WangYiYun()

def WangYiYunD(name):
    return 网易云点歌.MusicParse(name)
def QQD(name):
    return QQ点歌.MusicParse(name)

def on_GroupMessage(Message: MsgChain, sender: GroupInfo):
    mesg = Message.GetCQ()
    try:
        if mesg.startswith('点歌'):
            msg = MsgChain()
            msg.joinApp(WangYiYunD(mesg.replace('点歌','')))
            Send['sendGroupMsg'](sender.GroupId,msg)
    except:
        print('点歌异常！')

def Main(sendGroupMsg, SendFriendMsg):
    #传递回调函数
    Send['sendGroupMsg']=sendGroupMsg