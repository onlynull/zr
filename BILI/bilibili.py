from time import sleep
import json
import time

from requests import api
from .api import api_bilibili, api_live, api_vc
from Log import INFO,ERROR
from msgType import *
import os
from webserver import zr,apichecklogin,checklogin,request

#用于包目录下__init__.py引用本模块时直接 from .bilibili import * 导入的项目
__all__ = (
    'Main',             #此方法不可以注释，否则本模块将不会被添加进任务
    #'on_GroupMessage',  #不需要接收群消息时将此行注释既可
    #'on_FriendMessage'  #不需要接收私聊消息时将此行注释既可
    )

#用来存放发送消息回调，也可以通过其他方法保存
Send={'sendGroupMsg':None,'SendFriendMsg':None}

#配置文件路径
Configpath = os.path.dirname(os.path.realpath(__file__))+ '\config.json'
Configpath1 = os.path.dirname(os.path.realpath(__file__))+ '\config1.json'

#注册http的api接口
#index
@zr.route('/BILI',endpoint='BILIindex')
@checklogin
def index():
    return '<h>BILIBILI</h>'

#获取配置列表
@zr.route('/api/BILI/config',methods=['GET'],endpoint='BILIgetconfig')
def getconfig():
    try:
        file = open(Configpath1, mode='r', encoding='utf-8')
        config = json.load(file)
        file.close()
        return json.dumps({'code':200,'msg':'','data':config},ensure_ascii=False)
    except:
        text='读取配置文件或解析时发生异常，检查配置文件是否正确，默认路径为.BILI目录下的config.json。如果没有则需要复制文件 _config(将我复制改名为config.json).json 为 config.json'
        ERROR('HTTPAPI-'+text)
        return json.dumps({'code':500,'msg':'','data':text},ensure_ascii=False)

#设置配置列表
@zr.route('/api/BILI/config',methods=['POST'],endpoint='BILIsetconfig')
@apichecklogin
def setconfig():
    try:
        code=200
        msg = ''
        d=[]
        #校验传输过来的数据是否正确
        j = json.loads(request.get_data().decode())
        #检查必填数据是否填入
        if not j.get('delay'):
            code=500
            msg = '错误的delay'
        elif not j.get('config'):
            code=500
            msg = '错误config'
        elif len(j.get('config')) >= 1:
            #循环进入配置项检查
            for c in j['config']:
                #检查必填项
                if not c.get('uid'):
                    code=500
                    msg = '存在未填写uid的监听目标'
                    d.append(c)
                elif not c.get('Group'):
                    code=500
                    msg = '存在未填写推送群Group的监听目标'
                    d.append(c)
                elif len(c.get('Group')) >= 1:
                    for g in c['Group']:
                        if not g.get('id'):
                            code=500
                            msg = '存在未填写推送群GroupID的监听目标'
                            d.append(c)
        if code == 500:
            if d:
                err={'err':d}
            else:
                err={}
            return json.dumps({'code':code,'msg':msg,'data':err},ensure_ascii=False)
        file = open(Configpath1, mode='w', encoding='utf-8')
        file.write(json.dumps(j,ensure_ascii=False,indent=2))
        file.close()
        return json.dumps({'code':200,'msg':'写入成功','data':{}},ensure_ascii=False)
    except:
        '''异常'''
        print('BILIsetconfig-写入配置文件失败')
        return json.dumps({'code':500,'msg':'失败','data':{}},ensure_ascii=False)

class UserData:
    '''用户对象数据类型'''

    def __init__(
            self,
            uid:str,
            uname=None,
            showname=None,
            roomid=None,
            PushGroupInfo=None,
            Startvideo=False,
            StartLive=False,
            StartDynamic=False,
    ) -> None:
        '''将用户基础信息置入'''
        self.uid = uid
        self.uname = uname
        self.roomid = roomid
        self.showname = showname
        self.PushGroupInfo = PushGroupInfo
        self.StartVideo = Startvideo
        self.StartLive = StartLive
        self.StartDynamic = StartDynamic

    def GetName(self,newname=''):
        '''返回用于展示的昵称'''
        if newname:
            #更新用户昵称
            self.uname = newname
        return self.showname if self.showname else self.uname

class VideoData:
    '''视频信息数据类型'''

    def __init__(
            self,
            aid=None,  # 视频aid
            bvid=None,  # 视频bvid
            title=None,  # 标题
            pic=None,  # 封面
            pubdate=None,  # 更新时间
            desc=None,  # 简介
            owner_name=None,  # 作者名称
            view=0,  # 播放量
            danmaku_num=0,  # 弹幕数量
            reply_num=0,  # 评论量
            favorite=0,  # 收藏量
            cion=0,  # 投币量
            share=0,  # 分享量
            like=0,  # 点赞数
            dynamic_title=None,  # 动态标题
            tname=None,  # 分区名称
    ) -> None:
        self.aid = aid
        self.bvid = bvid
        self.title = title
        self.pic = pic
        self.pubdate = pubdate
        self.desc = desc
        self.owner_name = owner_name
        self.view = view
        self.danmaku_num = danmaku_num
        self.reply_num = reply_num
        self.favorite = favorite
        self.cion = cion
        self.share = share
        self.like = like
        self.dynamic_title = dynamic_title
        self.tname = tname

class LiveData:
    def __init__(
            self,
            roomid='',
            uid='',
            title='',  # 标题
            status=False,  # 状态
            area='',  # 分区
            pic='',  # 封面
            uname='',  # 昵称
            face='',  # 头像
            show_room_id='',  # 短号
            medal_name='',  # 勋章名
    ) -> None:
        self.roomid = roomid
        self.uid = uid
        self.title = title
        self.status = status
        self.area = area
        self.pic = pic
        self.uname = uname
        self.face = face
        self.show_room_id = show_room_id
        self.medal_name = medal_name

class DynamicData:
    '''将dict的数据传入，自动解析'''
    '''
    ' type对应的类型
    ' e.default = {
    ' ALL: 268435455,
    ' REPOST: 1,            #转发
    ' PIC: 2,               #相簿
    ' WORD: 4,              #文本
    ' VIDEO: 8,             #视频
    ' CLIP: 16,             #动态小视频
    ' DRAMA: 32,                #?广播
    ' ARTICLE: 64,          #专栏
    ' MUSIC: 256,           #音频
    ' BANGUMI: 512,             #?番剧
    ' NONE: 1024,               #
    ' H5_SHARE: 2048,       #网页分享
    ' COMIC_SHARE: 2049,        #?漫画分享
    ' FILM: 4098,               #?电影
    ' TV: 4099,                 #?电视剧
    ' DOCUMENTARY: 4101,        #?纪录片
    ' LIVE_ROOM: 4200,      #直播间
    ' LIVE: 4201,               #?开播
    ' MEDIA_LIST: 4300,         #?
    ' HOT: 1e3                  #?热门
    ' }
    '''
    pic = []
    vote = None
    msgtype = {
        1: '转发了',
        2: '相簿',
        4: '文本',
        8: '视频',
        16: '小视频',
        64: '专栏',
        256: '音乐',
        2048: '网页',
        4200: '直播间'
    }

    def __init__(self, card: dict,) -> None:
        desc = card['desc']
        self.dynamic_id = desc['dynamic_id']
        self.uid = desc['uid']
        self.type = desc['type']                            #动态类型
        self.rid = desc['rid']
        self.timestamp = desc.get('timestamp','')
        self.orig_dy_id = desc.get('orig_dy_id','')
        self.orig_type = desc.get('orig_type','')                #被转发的动态类型
        self.uname = desc['user_profile']['info']['uname']
        self.face = desc['user_profile']['info']['face']
        c = json.loads(card['card'])
        Dynamic_Type = {
            1: self.DT1,
            2: self.DT2,
            4: self.DT4,
            8: self.DT8,
            16: self.DT16,
            64: self.DT64,
            256: self.DT256,
            2048: self.DT2048,
            4200: self.DT4200
        }
        self.title, self.name = Dynamic_Type.get(self.type, self.DTO)(c)
        if self.type == 1:
            self.msg = '转发了' + self.msgtype.get(self.orig_type, '一个') + '动态'
        else:
            self.msg = '发布了' + self.msgtype.get(self.type, '一个') + '动态'
        extend_json = card.get('extend_json')
        if extend_json:
            extend = json.loads(extend_json)
            self.Dynamic_extend(extend)

    def DT1(self, card: dict):
        '''Type=1，转发动态'''
        name = card['user']['uname']
        title = card['item']['content']
        Dynamic_Type = {
            1: self.DT1,
            2: self.DT2,
            4: self.DT4,
            8: self.DT8,
            16: self.DT16,
            64: self.DT64,
            256: self.DT256,
            4200: self.DT4200
            # 2048: self.DT2048
        }
        orig = json.loads(card['origin'])
        orig_title, orig_name = Dynamic_Type.get(
            self.orig_type, self.DTO)(orig)
        return title+'\n'+'@'+orig_name+'\n'+orig_title, name

    def DT2(self, card: dict):
        '''Type=2，相簿动态'''
        #self.title = card['item']['description']
        title = card['item']['description']
        name = card['user']['name']
        pic = []
        for img in card['item']['pictures']:
            pic.append(img['img_src'])
        self.pic = pic
        return title, name

    def DT4(self, card: dict):
        '''Type=4，文本动态'''
        title = card['item']['content']
        name = card['user']['uname']
        return title, name

    def DT8(self, card: dict):
        '''Type=8，视频动态'''
        title = card['dynamic']+'\n'+card['title']
        name = card['owner']['name']
        pic = [card['pic']]
        self.pic = pic
        return title, name

    def DT16(self, card: dict):
        '''Type=16，动态小视频'''
        title = card['item']['description']
        name = card['user']['name']
        return title, name

    def DT64(self, card: dict):
        '''Type=64，专栏动态'''
        title = card['title']+'\n'+card['summary']
        name = card['author']['name']
        pic = [card['banner_url']]
        self.pic = pic
        return title, name

    def DT256(self, card: dict):
        '''Type=256，音频动态'''
        title = card['title']+'\n'+card['intro']
        name = card['upper']
        pic = [card['cover']]
        return title, name

    def DT2048(self, card: dict):
        '''Type=2048，网页分享动态'''
        title = card['sketch']['title']+'\n'+card['sketch']['desc_text']
        name = card['user']['uname']
        return title, name

    def DT4200(self, card: dict):
        '''Type=4200，直播间分享'''
        title = card['title']
        name = card['uname']
        pic = [card['cover']]
        self.pic = pic
        return title, name

    def DTO(self, card: dict):
        '''其他类型，其他未收集动态'''
        return '未知', '未知', '未知'

    def Dynamic_extend(self, extend: dict):
        '''扩展信息，包含一些发布动态时的定位信息，动态里投票信息等'''
        # print(extend)
        if extend.get('vote', {}).get('desc'):
            vote = []
            for op in extend['vote']['options']:
                vote.append(f'{op["desc"]}')
            self.vote = '扩展信息：投票信息(已有'+str(extend["vote"]["join_num"])+'人参加投票，每人最多可投'+str(extend["vote"]["choice_cnt"])+'票)\n'+extend["vote"]["desc"]+'\n'+'\n'.join(
                vote)+'\n投票地址：https://t.bilibili.com/vote/h5/index/#/result?vote_id='+str(extend["vote"]["vote_id"])

class bilibili_video:
    '''用户视频处理'''
    uid = ''
    videoaidlist = None
    newvideo = None
    api = api_bilibili()

    def __init__(self, uid) -> None:
        self.uid = uid
        vlist, self.videoaidlist = self.GetVideo()

    def GetVideo(self, ps=10):
        '''获取视频列表默认前10条详细信息的json列表和aid列表，网络错误，或者无作品返回None'''
        try:
            j = self.api.Getsearch(uid=self.uid, ps=ps).json()
        except Exception as e:
            ERROR(f'获取动态信息时发生异常，此处异常应先检查网络！异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            j = None
        videoaid = []
        if j and j.get('code') == 0:
            vlist = j.get('data', {}).get('list', {}).get('vlist', [])
            for v in vlist:
                videoaid.append(v['aid'])
            return vlist, videoaid
        else:
            return [], []

    def GetnewVideo(self):
        '''获取最新的一条视频videodata数据'''
        vlist, aidlist = self.GetVideo()
        if len(vlist) != 0:
            v = vlist[0]
            return VideoData(
                aid=v['aid'],
                bvid=v['bvid'],
                title=v['title'],
                pic=v['pic'],
                pubdate=v['created'],
                desc=v['description'],
                owner_name=['author']
            )
        else:
            return None

    def IsNewVideo(self):
        '''是否有新视频更新,如果更新返回True，和视频数据'''
        video = self.GetnewVideo()
        if video == None:
            return False, None
        newaid = video.aid
        if newaid in self.videoaidlist:
            '''表示最新获取到的存在列表里，则为未更新'''
            return False, None
        else:
            self.videoaidlist.append(newaid)
            return True, video

class bilibili_live:
    '''直播处理'''
    roomid = 0
    uid = 0
    oldLiveStatus = False  # 表示当前本地记录的状态
    RoomStatus = False  # 表示是否开通直播间
    roominfo = None
    api = api_live()

    def __init__(self, uid, roomid=None) -> None:
        '''也可以提交UID，自动获取roomid并完成相关数据获取'''
        self.uid = uid
        if roomid != None:
            self.roomid = roomid
            self.RoomStatus = True
        info = self.api.Get_Master_info(uid).json()
        if info:
            data = info.get('data', {})
            if data.get('room_id'):
                self.RoomStatus = True
                self.roomid = data['room_id']
                #j = api_live.Get_Info(self.roomid).json()
                self.roominfo = LiveData(
                    roomid=self.roomid,
                    uid=self.uid,
                    # title=j.get('data',{}).get('title',''),
                    # status=bool(j.get('data',{}).get('live_status',False)),
                    status=False,  # 初始化置入False，则可以在启动时就快速推送开播信息
                    # area=j.get('data',{}).get('parent_area_name',''),
                    # pic=j.get('data',{}).get('user_cover',''),
                    uname=data.get('info', {}).get('uname', ''),
                    face=data.get('info', {}).get('face', ''),
                    # show_room_id=j.get('data',{}).get('short_id',''),
                    medal_name=data['medal_name'])
                self.oldLiveStatus = self.roominfo.status
            else:self.RoomStatus = False

    def IsLive(self) -> bool:
        '''此方法判断返回是否开播，而不是当前直播状态'''
        if self.RoomStatus:
            try:
                j = self.api.Get_Info(self.roomid).json()
            except Exception as e:
                ERROR(f'获取直播间信息时发生异常，此处异常应先检查网络！异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
                j = None
            if j and j.get('code') == 0:
                data = j.get('data', {})
                live_status = bool(data.get('live_status', False))
                if live_status != self.oldLiveStatus:
                    self.oldLiveStatus = live_status
                    self.roominfo.status = live_status
                    if live_status:
                        # 更新直播间info
                        self.roominfo.area = data['parent_area_name'] + \
                            '·'+data['area_name']
                        self.roominfo.pic = data['user_cover']
                        self.roominfo.title = data['title']
                        self.roominfo.show_room_id = data['short_id']
                    return live_status
                else:
                    self.oldLiveStatus = live_status
                    self.roominfo.status = live_status
                    return False
                '''废弃逻辑
                if bool(data.get('live_status',False)) == self.oldLiveStatus:
                    #表明记录的状态并没有改变，不做开播判断
                    return False
                elif data.get('live_status',False):
                    #表明直播间状态live_status=1，开播，且本地记录状态为False
                    self.oldLiveStatus=True
                    self.roominfo.status=True
                    return True
                else:
                    self.roominfo.status=False
                    self.oldLiveStatus=False
                    return False
                '''
            else:
                return False
        else:
            return False

class bilibii_dynamic:
    '''动态处理'''
    uid = ''
    dynamicidlist = None
    api = api_vc()

    def __init__(self, uid) -> None:
        self.uid = uid
        cards, self.dynamicidlist = self.GetDynamic()

    def GetDynamic(self):
        '''获取动态列表默认前10条详细信息的json列表和dynamicid列表，网络错误，或者无作品返回None'''
        try:
            j = self.api.Get_space_history(self.uid).json()
        except Exception as e:
            ERROR(f'获取动态信息时发生异常，此处异常应检查网络！异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            j = None
        Dynamicid = []
        if j and j.get('code') == 0:
            cards = j.get('data', {}).get('cards', [])
            for d in cards:
                Dynamicid.append(d['desc']['dynamic_id'])
            return cards, Dynamicid
        else:
            return [], []

    def GetNewDynamic(self):
        '''获取最新的一条动态'''
        cards,cardid = self.GetDynamic()
        if len(cards) != 0:
            return DynamicData(card=cards[0])
        else:
            return None

    def IsNewDynamic(self):
        '''是否有新动态更新，如果更新返回True，和动态数据'''
        dynamic = self.GetNewDynamic()
        if dynamic == None:
            return False, None
        newdynamicid = dynamic.dynamic_id
        if newdynamicid in self.dynamicidlist:
            '''表示最新获取到的存在列表里，则为未更新'''
            return False, None
        else:
            self.dynamicidlist.append(newdynamicid)
            return True, dynamic

class bilibili_user:
    '''B站用户监听处理类'''
    user = None

    def __init__(self, user: UserData) -> None:
        self.user = user
        if self.user.StartVideo:
            self.video = bilibili_video(uid=self.user.uid)
        if self.user.StartDynamic:
            self.dynamic = bilibii_dynamic(uid=self.user.uid)
        if self.user.StartLive:
            self.live = bilibili_live(uid=self.user.uid, roomid=self.user.roomid)
            # 更新昵称
            if self.live.RoomStatus:
                self.user.uname = self.live.roominfo.uname
        INFO(f'用户：{self.user.GetName()}[{self.user.uid}] 初始化完成！')

def run_task():
    #循环的在try下运行
    while True:
        try:
            # 读入配置文件
            INFO('读入配置文件...')
            try:
                file = open(Configpath, mode='r', encoding='utf-8')
                config = json.load(file)
                file.close()
            except:
                ERROR('读入配置文件或解析时发生异常，检查配置文件是否正确，默认路径为.BILI目录下的config.json。如果没有则需要复制文件 _config(将我复制改名为config.json).json 为 config.json')
                return
            # 初始化
            INFO('开始初始化所有需要监听的用户')
            user = []
            user.clear()
            delay = config['delay']
            forward_draw = config.get('forward_draw',False)
            for u in config['config']:
                user.append(bilibili_user(UserData(uid=u['uid'], uname=u.get('uname'), showname=u.get('showname'),roomid=u.get('roomid'),PushGroupInfo=u['Group'],
                                                StartDynamic=u['StartDynamic'], StartLive=u['StartLive'], Startvideo=u['Startvideo'])))
                sleep(0.2)
            INFO('所有用户初始化完成')
            INFO('开始执行监听任务')
            INFO('用户列表：'+','.join(list(map(str,[u.user.uid for u in user]))))
            if len(user) == 0:
                INFO('没有载入任何需要监听的用户')
                return
            #执行任务
            while True:
                #循环执行任务！
                errN = 0    #用于记录异常次数，超过十次则跳出while True 循环重新加载
                try:
                    for u in user:
                        #延迟
                        sleep(delay)

                        #检查是否投稿
                        if u.user.StartVideo:   #是否启用视频监听
                            Y,Data = u.video.IsNewVideo()
                            if Y:
                                INFO(f'{u.user.GetName()}更新了视频，准备推送。')
                                for group in u.user.PushGroupInfo:
                                    msg = MsgChain()
                                    if group.get('ATall'):
                                        msg.joinAT(-1)
                                    msg.joinPlain(f'你的小可爱{u.user.GetName(Data.owner_name)}有新的作品发布了哟~\n{Data.title}\n{Data.desc}\n')
                                    if group.get('sendPic'):
                                        msg.joinImg(Url=Data.pic) 
                                    if group.get('sendUrl'):
                                        msg.joinPlain('https://www.bilibili.com/video/'+str(Data.bvid))
                                    Send['sendGroupMsg'](group.get('id',0),msg)

                        #检查是否开播
                        if u.user.StartLive:    #是否启用直播监听
                            Y=u.live.IsLive()
                            if Y:
                                INFO(f'{u.user.GetName()}开播了，准备推送。')
                                for group in u.user.PushGroupInfo:
                                    msg = MsgChain()
                                    if group.get('ATall'):
                                        msg.joinAT(-1)
                                    msg.joinPlain(f'你的小可爱{u.user.GetName()}开播啦~\n{u.live.roominfo.title}\n{u.live.roominfo.area}')
                                    if group.get('sendPic'):
                                        msg.joinImg(Url=u.live.roominfo.pic) 
                                    if group.get('sendUrl'):
                                        msg.joinPlain('https://live.bilibili.com/'+str(u.live.roominfo.roomid))
                                    Send['sendGroupMsg'](group.get('id',0),msg)

                        #检查是否发布新动态
                        if u.user.StartDynamic: #是否启用动态监听
                            Y,Data = u.dynamic.IsNewDynamic()
                            if Y:
                                INFO(f'{u.user.GetName()}更新了动态，准备推送。')
                                #检查是否为转发的抽奖动态
                                if Data.orig_type == 2 and Data.title.find('互动抽奖') != -1 and forward_draw == False:
                                    INFO(f'{u.user.GetName()}的动态内容为转发内容：{Data.title}。\n被判断为转发的抽奖动态，不发送。如果需要发送请在设置里把 forward_draw改为true。如果没有此选项在delay下面添加既可')
                                else:
                                    for group in u.user.PushGroupInfo:
                                        msg = MsgChain()
                                        if group.get('ATall'):
                                            msg.joinAT(-1)
                                        msg.joinPlain(f'你的小可爱{u.user.GetName(Data.uname)}{Data.msg}\n{Data.title}')
                                        if group.get('sendPic'):
                                            for pic in Data.pic:
                                                msg.joinImg(Url=pic)
                                        if group.get('sendUrl'):
                                            msg.joinPlain('https://t.bilibili.com/'+str(Data.dynamic_id))
                                        Send['sendGroupMsg'](group.get('id',0),msg)
                except Exception as e:
                    ERROR(f'执行任务期间发生异常，异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
                    errN += 1
                if errN == 10:
                    #for循环体出现10次异常，重启任务
                    break
                #循环固定延时
                time.sleep(2)
        except Exception as e:
            ERROR(f'运行时发生异常，将重新启动任务。异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            #防止一直出错
            time.sleep(10)

def Main(sendGroupMsg,SendFriendMsg):
    '''启动程序，并传入消息发送的回调函数'''
    #保存回调函数
    Send['sendGroupMsg']=sendGroupMsg
    Send['SendFriendMsg']=SendFriendMsg
    run_task()

def on_GroupMessage(Message:MsgChain,sender:GroupInfo):    
    print('bili收到群消息',Message.GetCQ())

def on_FriendMessage(Message:MsgChain,sender:SenderInfo):
    print('bili收私聊消息',Message.GetCQ())