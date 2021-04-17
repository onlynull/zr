import requests,json,time,os
from Log import INFO,ERROR
from msgType import MsgChain

__all__ = (
    'Main',             #此方法不可以注释，否则本模块将不会被添加进任务
    #'on_GroupMessage',  #不需要接收群消息时将此行注释既可
    #'on_FriendMessage'  #不需要接收私聊消息时将此行注释既可
    )

#用来存放发送消息回调，也可以通过其他方法保存
Send={'sendGroupMsg':None,'SendFriendMsg':None}

#配置文件路径
Configpath = os.path.dirname(os.path.realpath(__file__))


class dy:
    def __init__(self,conf:dict):
        self.conf=conf
        self.sec_uid = conf['sec_uid']
        self.name = conf['showname']
        if not self.GetInfo():
            '''secuid验证失败'''
            ERROR(f'{conf}：的sec_uid无效')
        self.vid=[].copy()

    def GetInfo(self):
        try:
            r = requests.get('https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid='+self.sec_uid)
            if r.status_code == 200:
                j = r.json()
                if j['status_code'] == 0:
                    self.name = j['user_info']['nickname']
                    return True
            return False
        except:
            ERROR(f'获取用户信息时发生异常')
            return False
    
    def Getaweme(self):
        '''获取作品列表'''
        url='https://www.iesdouyin.com/web/api/v2/aweme/post/?count=10&sec_uid='+self.sec_uid
        try:
            r = requests.get(url)
            if r.status_code == 200:
                j = r.json()
                return j['aweme_list']
            return []
        except:
            ERROR(f'获取用户视频列表时发生异常')
            return []
    
    def check(self):
        '''检查是否更新'''
        j = self.Getaweme()
        if not self.vid and len(j) != 1:
            for v in j:
                self.vid.append(v.get('video',{}).get('vid'))
            return False
        if j :
            for v in j:
                video = v.get('video',{})
                vid = video.get('vid')
                if vid in self.vid:
                    #当前视频在本地记录过，直接跳出循环既可
                    pass
                else:
                    #未记录，表示为新视频
                    INFO(f'用户{self.conf.get("showname",self.name)}有新作品了')
                    self.msg = MsgChain()
                    self.msg.joinPlain(f'【抖音】{self.conf.get("showname",self.name)}更新视频啦~\n{v.get("desc")}')
                    self.msg.joinImg(Url=video.get('origin_cover',{}).get('url_list',['1'])[0])
                    self.msg.joinPlain(video.get('play_addr',{}).get('url_list',['1'])[1])
                    self.video = MsgChain().joinVideo(Url=video.get('play_addr',{}).get('url_list',['1'])[1])
                    self.vid.append(vid)
                    return True
        return False

def run():
    INFO('读入配置文件...')
    try:
        file = open(Configpath + '\config.json', mode='r', encoding='utf-8')
        config = json.load(file)
        file.close()
    except:
        ERROR('读入配置文件或解析时发生异常，检查配置文件是否正确，默认路径为.douyin目录下的config.json。如果没有则需要复制文件 _config(将我复制改名为config.json).json 为 config.json')
        return
    INFO('开始初始化所有需要监听的抖音用户')
    user = []
    user.clear()
    delay = int(config['delay'])
    for u in config['config']:
        if u.get('sec_uid'):
            user.append(dy(u))
        else:
            ERROR(f'{u}未填写sec_uid')
        if len(user) == 0:
            INFO('没有载入任何需要监听的用户')
            return
    INFO('开始轮询抖音')
    i = 0
    while True:
        for u in user:
            #print(u.vid)
            if u.check():
                for g in u.conf['Group']:
                    Send['sendGroupMsg'](g,u.msg)
                    Send['sendGroupMsg'](g,u.video)
            time.sleep(delay)
        time.sleep(5)
        

def Main(sendGroupMsg, SendFriendMsg):
    #传递回调函数
    Send['sendGroupMsg']=sendGroupMsg
    run()