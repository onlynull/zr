import requests
from requests.models import Response
import json
from Log import ERROR

ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'


class api_live:
    '''api.live.bilibili.com下的接口'''
    h = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': 'https://live.bilibili.com/',
        #'sec-ch-ua':'"Google Chrome";v="87"',
        'user-agent': ua
    }

    def Get_anchor_in_room(self, roomid):
        '''通过roomid获得uid、昵称、LV等级、UL等级、UP等级'''
        url = 'https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room?roomid=' + \
            str(roomid)
        return requests.get(url=url, headers=self.h)

    def Get_Info(self, roomid):
        '''通过ROOMID获取直播间信息,支持短号'''
        url = 'https://api.live.bilibili.com/room/v1/Room/get_info?room_id=' + \
            str(roomid)
        try:
            r = requests.get(url=url, headers=self.h)
        except Exception as e:
            ERROR(f'Request访问时发生异常：。异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            r = Response()
        return r

    def Get_RoundPlayVideo(self, roomid):
        '''通过ROOMID获取直播间当前轮播的视频aid'''
        url = 'https://api.live.bilibili.com/live/getRoundPlayVideo?room_id=' + \
            str(roomid)
        return requests.get(url=url, headers=self.h)

    def Get_BannedInfo(self, roomid):
        '''通过ROOMID获取直播间封禁时间'''
        url = 'https://api.live.bilibili.com/room/v1/Room/getBannedInfo?roomid=' + \
            str(roomid)
        return requests.get(url=url, headers=self.h)

    def Get_RoomInfoOld(self, uid):
        '''通过UID获取直播间信息,可获得roomStatus、roundStatus、liveStatus、title、roomid'''
        url = 'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid=' + \
            str(uid)
        return requests.get(url=url, headers=self.h)

    def Get_Card_user(self, uid):
        '''通过UID获取当前此用户佩戴勋章、头衔、UL、follow_num、姥爷、勋章等级'''
        url = 'https://api.live.bilibili.com/live_user/v1/card/card_user?ruid=1&uid=' + \
            str(uid)
        return requests.get(url=url, headers=self.h)

    def Get_Master_info(self, uid):
        '''通过UID获得昵称、UP等级、roomid、开通的勋章名、直播间公告、性别'''
        url = 'https://api.live.bilibili.com/live_user/v1/Master/info?uid=' + \
            str(uid)
        try:
            r = requests.get(url=url, headers=self.h)
        except Exception as e:
            ERROR(f'Request访问时发生异常：。异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            r = Response()
        return r
    
    def Get_RoomS_info(self, roomids:list):
        '''批量获得所有直播间info，包括开播状态'''
        url = 'https://api.live.bilibili.com/room/v2/Room/get_by_ids'
        data={'ids':roomids}
        try:
            r = requests.post(url=url, data=json.dumps(data), headers=self.h)
        except Exception as e:
            ERROR(f'Request访问时发生异常：。异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            r = None
        return r

    def Get_Danmu_getConf(self):
        '''获取websocket地址'''
        url = 'https://api.live.bilibili.com/room/v1/Danmu/getConf'
        return requests.get(url=url, headers=self.h)


class api_vc:
    '''api.vc.bilibili.com下面的接口，动态相关的接口'''
    h = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        #'sec-ch-ua':'"Google Chrome";v="87"',
        'user-agent': ua
    }

    def Get_space_history(self, uid):
        '''通过UID获得10条此用户的动态信息'''
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?&host_uid=' + \
            str(uid)
        try:
            r = requests.get(url=url, headers=self.h)
        except Exception as e:
            ERROR(f'Request访问时发生异常：。异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            r = Response()
        return r

    def Get_dynamic_detail(self, dynamic_id):
        '''获取动态的详细信息'''
        url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id=' + \
            str(dynamic_id)
        return requests.get(url=url, headers=self.h)

    def Get_detail(self, doc_id):
        '''通过相簿ID获取类型为相簿的动态信息'''
        url = 'https://api.vc.bilibili.com/link_draw/v1/doc/detail?doc_id=' + \
            str(doc_id)
        return requests.get(url=url, headers=self.h)

    def name_to_uid(self, name: str):
        '''通过用户昵称获取UID'''
        url = 'https://api.vc.bilibili.com/dynamic_mix/v1/dynamic_mix/name_to_uid?names='+name
        return requests.get(url=url, headers=self.h)


class api_bilibili:
    '''api.bilibili.com下接口，为主站及个人主页类的接口。此api容易被风控'''
    h = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        #'sec-ch-ua':'"Google Chrome";v="87"',
        'referer': 'https://space.bilibili.com/',
        'user-agent': ua
    }

    def Getsearch(self, uid, ps=10):
        '''通过UID获取作品列表默认为前10个'''
        url = f'https://api.bilibili.com/x/space/arc/search?mid={str(uid)}&pn=1&ps={str(ps)}'
        try:
            r = requests.get(url=url, headers=self.h)
        except Exception as e:
            ERROR(f'Request访问时发生异常：。异常信息:{e.__doc__} 文件：{e.__traceback__.tb_frame.f_globals["__file__"]} 行号：{str(e.__traceback__.tb_lineno)}')
            r = Response()
        return r

    def GetSpaceInfo(self, uid):
        '''通过UID获得用户昵称、性别、头像、签名、LV等级、个人认证、会员信息、主页头图、直播间信息（是否开通、直播状态、轮播状态、直播间号、封面、标题）'''
        url = 'https://api.bilibili.com/x/space/acc/info?mid='+str(uid)
        return requests.get(url=url, headers=self.h)

    def Get_video_view(self, aid=None, bvid=None):
        '''通过aid或者bvid获取视频信息'''
        if aid == None:
            url = 'https://api.bilibili.com/x/web-interface/view?bvid='+bvid
        else:
            url = 'https://api.bilibili.com/x/web-interface/view?aid='+str(aid)
        return requests.get(url=url, headers=self.h)
