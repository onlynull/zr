# -*- coding: utf-8 -*-
from Log import ERROR, INFO
import requests
from msgType import MsgChain
import time

class Acfun:
    InfoUrl = 'https://api-new.app.acfun.cn/rest/app/live/info'
    ProfileUrl = 'https://api-new.app.acfun.cn/rest/app/feed/profile'
    LiveExtra_infoUrl = 'https://live.acfun.cn/api/liveExtra/info'
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'}
    Uid = None
    Name = None
    OldVideo = None#储存的最新的video，如果与video第一个不是同一个则表示UP更新视频了
    OldDynamic = None#储存的最新的Dynamic，如果与Dynamic第一个不是同一个则表示UP更新视频了
    Video = None
    Dynamic = None
    UserInfo = None
    ''' UserInfo 信息
    主播名称：name
    主播签名：signature
    主播头像：headUrl
    签约信息：verifiedText
    主播粉丝数int:fanCountValue
    主播关注数int：followingCountValue
    '''
    Live = False
    OldLive = False
    LiveInfo = None
    HTTP = None
    user = None
    DynamicID = None #动态ID列表，防止用户删除动态导致的误报
    VideoID = None #视频ID列表，防止用户删除视频导致的误报
    def __init__(self,user):
        self.user = user
        self.Uid = str(user['uid'])
        self.HTTP = requests.session()
        self.HTTP.auth = ('user','pass')
        self.HTTP.headers.update(self.header)
        #self.Getinfo()
        #self.GetDynamic()
    
    def Getinfo(self):
        '''获取主播信息以及作品、是否开播信息'''
        r = self.HTTP.get(url=self.InfoUrl, params = {'authorId':self.Uid})
        if r.status_code == 200:
            json = r.json()
            #获取UP信息
            user = json.get('user',{})
            if user != None:
                self.UserInfo = user
                self.Name = self.UserInfo.get('name',"")
            #判断是否开播
            self.LiveInfo = json
            if json.get('liveId'):
                self.Live = True
            else:
                self.Live = False
        
        #更换地址了，要分开查询
        r = self.HTTP.get(url=self.LiveExtra_infoUrl, params = {'authorId':self.Uid})
        if r.status_code == 200:
            json = r.json()
            #获取作品信息
            Video = json.get('contributeList',{}).get('feed',[{}])
            self.Video = Video if Video != [] else [{}]
            #print(self.Video)
            #print(self.Name)
            #查看OldVideo信息是否含有有效信息,如果没复制则将此时获取到的第一条赋值进去
            if self.OldVideo == None:
                self.OldVideo = self.Video[0]
                #print(self.OldVideo)
            if self.VideoID == None:
                #注入视频ID列表
                self.VideoID = []
                if self.Video[0] != {}:
                    for v in self.Video:
                        self.VideoID.append(v.get('dougaId',0))

    def GetDynamic(self):
        ''''获取主播最新的3条动态'''
        r = self.HTTP.get(url=self.ProfileUrl, params = {'userId':self.Uid, 'count':5})#如果获取太多条数据量太高了，会影响速度
        if r.status_code == 200:
            Dynamic = r.json().get('feedList',[{}])
            self.Dynamic = Dynamic if Dynamic != [] else [{}]
            if self.OldDynamic == None:
                self.OldDynamic = self.Dynamic[0]
                #print(self.OldDynamic)
            if self.DynamicID == None:
                #注入动态ID列表
                self.DynamicID = []
                if self.Dynamic[0] != {}:
                    for d in self.Dynamic:
                        self.DynamicID.append(d.get('resourceId',0))
    
    def IsNewVideo(self) -> bool:
        '''判断视频是否更新'''
        if self.OldVideo.get('dougaId') != None and self.Video[0].get('dougaId') != None:
            #当两个值都不能为空时才能作为有效的数据进行判断
            if self.OldVideo['dougaId'] != self.Video[0]['dougaId']:
                #两个数据不相同,表明视频列表被刷新，更新Oldvideo数据，并判断此次最新一条是否为删除原第一条数据后的第二条，尝试在旧列表中寻找他
                self.OldVideo = self.Video[0]
                if self.OldVideo.get('dougaId') in self.VideoID:
                    #表示此条并非最新，而是第一条数据被删除，他成为的第一条，不能算是新动态，清空列表，等待下次获取动态时刷新他
                    INFO(f'用户{self.Name}似乎删除了一条视频，清空列表，等待下次查询时刷新')
                    self.VideoID = None  #动态数据有变动，清空列表，等待下次刷新
                    return False
                else: 
                    self.VideoID = None  #动态数据有变动，清空列表，等待下次刷新
                    return True
        return False

    def IsNewLive(self) -> bool:
        #因为网络波动，一律返回false,且不处理
        if self.LiveInfo == {}:
            return False
        if self.Live and self.OldLive == False:
            self.OldLive = True
            return True
        else: 
            self.OldLive = self.Live
            return False

    def IsNewDynamic(self) -> bool:
        '''判断动态是否更新'''
        if self.OldDynamic.get('resourceId') != None and self.Dynamic[0].get('resourceId') != None:
            if self.OldDynamic['resourceId'] != self.Dynamic[0]['resourceId']:
                self.OldDynamic = self.Dynamic[0]
                if self.OldDynamic.get('resourceId') in self.DynamicID:
                    INFO(f'用户{self.Name}似乎删除了一条动态，清空列表，等待下次查询时刷新')
                    self.DynamicID = None
                    return False
                else: 
                    self.DynamicID = None
                    return True
        return False

    def VideoLoad(self) -> MsgChain:
        '''载入将要推送的视频信息为MsgChain消息格式'''
        Msg = MsgChain()
        if self.user.get('ATall'):
            Msg.joinAT(-1)
            Msg.joinPlain(" \n")
        times = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(int(self.OldVideo['createTimeMillis'])/1000)))
        tags = []
        for tag in self.OldVideo['tagList']:
            tags.append(f'#{tag["name"]}#')
        Msg.joinPlain(f'你的小可爱{self.Name}有新作品了哦，快来看看吧~\n{self.OldVideo["title"]}\n{self.OldVideo["channel"]["parentName"]}·{self.OldVideo["channel"]["name"]} {times}')
        Msg.joinImg(Url=self.OldVideo['coverUrl'])
        Msg.joinPlain(f'{self.OldVideo["description"]}\n{" ".join(tags)}\n{self.OldVideo["shareUrl"]}')
        return Msg

    def DynamicOriginalLoad(self,Dynamic) -> MsgChain:  #将动态数据交给我解析，不要外部调用
        Msg = MsgChain()
        #print(Dynamic['resourceType'] , Dynamic['tagResourceType'])
        if int(Dynamic['resourceType']) == 10 and int(Dynamic['tagResourceType']) == 3:  #纯动态（原创、转发）
            moment = Dynamic['moment']
            Msg.joinPlain(moment.get('replaceUbbText')) #当为纯动态时，此条数据好像是必有的,动态的详细文本内容，无论是含图片动态还是转发动态，都会有的
            if int(moment['originResourceType']) == 0:  #originResourceType=0为原创，否则为转发
                momentType = moment['momentType']
                if int(momentType) == 2: #2是含图片动态，1是纯文本内容。因为无论类型为1还是2文本都会存在，这里就只判断类型为2的时候取出图片了
                    for img in moment['imgs']:
                        Msg.joinImg(Url=img['originUrl'])
            else:  #为转发动态，将转发的内容repostSource再次解析,这里的套娃只有一次
                Msg.joinPlain('\n------------------------------\n') #转发分割线
                Msg = Msg + self.DynamicOriginalLoad(Dynamic['repostSource'])
        elif int(Dynamic['resourceType']) == 2 and int(Dynamic['tagResourceType']) == 2:#视频动态
            Msg.joinPlain(f'{Dynamic["caption"]}\n{Dynamic["channel"]["parentName"]}·{Dynamic["channel"]["name"]}')
            Msg.joinImg(Url=Dynamic['coverUrl'])
        elif int(Dynamic['resourceType']) == 3 and int(Dynamic['tagResourceType']) == 1:#文章动态
            #略略略
            Msg.joinPlain(f'分类：{Dynamic["channel"]["parentName"]}·{Dynamic["channel"]["name"]}\n{Dynamic["articleTitle"]}\n{Dynamic["articleBody"]}')
            articleBodyImgsWithFormat = Dynamic.get('articleBodyImgsWithFormat')
            if len(articleBodyImgsWithFormat) > 0:
                for imgs in articleBodyImgsWithFormat:
                    if imgs['size'] > 2000000: #当图片大于2M时选择发送压缩后的图，否则发送原图
                        Msg.joinImg(Url=imgs['expandedUrl'])
                    else:Msg.joinImg(Url=imgs['originUrl'])
        #当都不符合要求是，看来又他妈的出现新的动态类型
        return Msg

    def DynamincLoad(self) -> MsgChain:
        '''载入将要推送的动态信息为MsgChain消息格式'''
        Msg = MsgChain()
        #判断一下是否有数据
        if self.OldDynamic.get('resourceId') == None:
            ERROR("获取到的数据有问题，无法正常推送。")
            return Msg
        Type = self.OldDynamic.get('moment',{}).get('originResourceType')
        if self.user.get('ATall'):
            Msg.joinAT(-1)
            Msg.joinPlain(" \n")
        if  not Type:
            Msg.joinPlain(f'你的小可爱{self.Name}发布一条新动态了哦，快来看看吧~\n')
        else:
            Msg.joinPlain(f'你的小可爱{self.Name}转发一条新动态了\n')
        Msg = Msg + self.DynamicOriginalLoad(self.OldDynamic)
        Msg.joinPlain('\n' + self.OldDynamic['shareUrl'])
        return Msg

    def LiveLoad(self) -> MsgChain:
        '''开播推送信息'''
        if self.Live == False:#为开播，不发送
            ERROR("主播未开播，无法载入相关信息")
            return MsgChain()
        Msg = MsgChain()
        if self.user.get('ATall'):
            Msg.joinAT(-1)
            Msg.joinPlain(" \n")
        Msg.joinPlain(f'你的小可爱[{self.Name}]开播啦~\n{self.LiveInfo.get("title","")}\n{self.LiveInfo.get("type",{}).get("name","")}\nhttps://live.acfun.cn/live/{self.Uid}')
        Msg.joinImg(Url=self.LiveInfo.get('coverUrls',[""])[0])
        return Msg
