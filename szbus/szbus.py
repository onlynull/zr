import time,os,requests
from .aip.ocr import AipOcr
from PIL import Image, ImageDraw, ImageFont
from Log import INFO,ERROR
from msgType import MsgChain,GroupInfo

__all__ = (
    'Main',  # 此方法不可以注释，否则本模块将不会被添加进任务
    'on_GroupMessage',  # 不需要接收群消息时将此行注释既可
    #'on_FriendMessage'  # 不需要接收私聊消息时将此行注释既可
)

# 用来存放发送消息回调，也可以通过其他方法保存
Send = {'sendGroupMsg': None, 'SendFriendMsg': None}

#当前模块路径
Mpath = os.path.dirname(os.path.realpath(__file__))


dayyanse={'周一':'#87CEEB','周二':'#00BFFF','周三':'#1E90FF','周四':'#4169E1','周五':'#6495ED','周六':'#0000FF','周日':'#8A2BE2'}

'''
#print(baiduocr.basicGeneral('http://jtj.suzhou.gov.cn/szinf/vercode/getVerifyCode'))
baiduocr = AipOcr('15399687','cycawH6kaNnDelKMUkr7u9Y7','TZ2FoNwVjGO7G0dkQGNof3yp9Uaz50dP')
hh={
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'jtj.suzhou.gov.cn',
    'Referer': 'http://jtj.suzhou.gov.cn/szjt/gjztcx/gjztcx.shtml',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
    }
r = requests.get('http://jtj.suzhou.gov.cn/szinf/vercode/getVerifyCode?1603073719629',headers=hh).content
with open('123.png','wb') as f:
    f.write(r)
bb = baiduocr.basicGeneral(r)
print(bb,bb['words_result'][0]['words'])
print(str(int(time.time()*1000)))
'''

def GetTianQi():
    '''获取苏州天气,高德地图'''
    try:
        dd=['','一','二','三','四','五','六','七']
        url='http://restapi.amap.com/v3/weather/weatherInfo?key=0e676d97c98483d5d1cce212bcd1b99e&city=320500&extensions=all'
        r = requests.get(url).json()
        if r and len(r['forecasts']) >= 1:
            l = r['forecasts'][0]['casts'][0]
            day = '周'+dd[int(l['week'])]
            if l['daywind'] == '无风向':
                风 = '无风'
            else:
                风 = l['daywind']+'风 '+l['daypower']+'级'
            s = f'{day} {l["dayweather"]} {l["nighttemp"]}-{l["daytemp"]}℃ {风}'
            return s
        return None
    except:
        return None

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

class szbus():
    baiduocr = None
    p = {
        #'http':'http://127.0.0.1:8888'
        }
    def __init__(self) -> None:
        self.baiduocr = AipOcr('15399687','cycawH6kaNnDelKMUkr7u9Y7','TZ2FoNwVjGO7G0dkQGNof3yp9Uaz50dP')
        #生成会话
        self.session = requests.Session()
        self.session.auth = ('user','pass')
        self.setCookies()

    def setCookies(self):
        h={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'jtj.suzhou.gov.cn',
        'Referer': 'http://jtj.suzhou.gov.cn/szjt/gjztcx/gjztcx.shtml',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
        }
        self.session.get('http://jtj.suzhou.gov.cn/szsfront/jtj/gjcx.jsp',headers=h,proxies=self.p)
        

    def GetGuid(self,Line):
        '''获取线路'''
        h={
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'jtj.suzhou.gov.cn',
        'Referer': 'http://jtj.suzhou.gov.cn/szsfront/jtj/line.jsp',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
        }
        json = self.session.post(f'http://jtj.suzhou.gov.cn/szinf/interfaceJtj/gjxlcx?LineName={str(Line)}',headers=h,proxies=self.p).json()
        #print('线路列表',json)
        if json:
            lineinfoL=[]
            lineinfoName=[]
            for lineinfo in json['data_original']['LineInfo']:
                if str(lineinfo['LName']) == str(Line):
                    lineinfoL.append(lineinfo['Guid'])
                    a = f'【{lineinfo["LFStdName"]}→{lineinfo["LEStdName"]}】\n【运营时间'
                    t = f'：{lineinfo["LFStdFTime"]}-{lineinfo["LFStdETime"]}】'
                    l = len(a) - 6 #首行长度
                    if len(t) / 2 + 6 > l:
                        l = len(t) / 2 + 6 
                    b = {'text':a,'color':"#000000",'len':l,'time':t}
                    #print(b)
                    lineinfoName.append(b)
            return lineinfoL,lineinfoName
        else:
            return None,None

    def GetCode(self,lGUID):
        '''获取验证码,返回验证码图片'''
        h={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
        }
        r = self.session.get(f'http://jtj.suzhou.gov.cn/szinf/vercode/getVerifyCode?{str(int(time.time()*1000))}',headers=h,proxies=self.p).content
        return r
    
    def OCRCOde(self,r):
        json =  self.baiduocr.basicGeneral(r)
        code = None
        if json:
            try:
                code = json['words_result'][0]['words']
                pass
            except:
                code = None
                pass
        return code
    
    def GetLineStatus(self,GUID,code):
        '''获取公交车线路状态,返回处理好的文本列表'''
        h={
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'jtj.suzhou.gov.cn',
        'Origin': 'http://jtj.suzhou.gov.cn',
        'Referer': f'http://jtj.suzhou.gov.cn/szsfront/jtj/line.jsp?LineGuid={GUID}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        }
        url = f'http://jtj.suzhou.gov.cn/szinf/interfaceJtj/gjxlxxcx?LineGuid={GUID}&verifyCodeValue={code}'
        return self.session.post(url,headers=h,proxies=self.p).json()
    
    def loadLineStatus(self,json,other=None):
        StandInfo = json.get('StandInfo')
        if json and StandInfo:
            sss = []
            H = 0
            #print(other)
            tianqi = GetTianQi()
            Maxssl = 0  #单行最大长度
            if tianqi != None:
                sss.append({'text':tianqi,'color':dayyanse.get(tianqi[0:2],'#DC143C'),'len':len(tianqi),'time':None})
                if len(tianqi) > Maxssl:
                    Maxssl = len(tianqi) #单行最大长度
                H = H + 1
            if other:
                sss.append(other)
                Maxssl = other['len'] #单行最大长度
                H = H + 2
                #print(Maxssl)
            for s in StandInfo:
                ss={}
                H = H + 1
                if s.get('InTime') == '':
                    ss['text'] = f'{s["SName"]}'
                    ss['color'] = "#000000"
                    ss['len'] = len(ss['text'])
                    ss['time'] = None
                else:
                    #ss['text'] = f'{s["SName"]}\n   进站时间：{s["InTime"]}({s["BusInfo"]})'
                    t = s["InTime"].split(' ')
                    ss['text'] = f'{s["SName"]}'
                    ss['color'] = '#FF69B4'
                    ss['len'] = len(ss['text'])   #备注名肯定比站名长，因为这里换行了，所以只取备注长度
                    ss['time'] = f'({t[1]})'
                if Maxssl < ss['len']:
                    Maxssl = ss['len']
                #print(Maxssl)
                sss.append(ss)
            return sss,Maxssl,H
        else:
            return None,None,None

    def MakePic(self,sss,Maxssl,H):
        fontc = 16
        setfont = ImageFont.truetype(Mpath+'\\fz.ttf',fontc)
        im = Image.new('RGB',(int(fontc*Maxssl+20),int(H*(fontc+5))+10),(255,255,255))
        dr = ImageDraw.Draw(im)
        i = 0
        #print("行数",H)
        for s in sss:
            if s['time'] != None:
                ss = s['text'] + s['time']
            else:
                ss = s['text']            
            dr.text((10,int(i*(fontc+5)+5)),ss,font=setfont,fill=s['color'])

            if s['text'].count('\n') >= 1:
                i = i + 2
            else:
                i = i + 1 
        name = f'{Mpath}\\pic\\{str(int(time.time()*1000))}.png'
        im.save(name)
        return name
    
    def MakePic_(self,sss,Maxssl,H):
        '''横向制图'''
        fontc = 16
        setfont = ImageFont.truetype(Mpath+'\\fz.ttf',fontc)
        im = Image.new('RGB',(int(H*(fontc+5))+10,int((fontc+5)*Maxssl+20)),(255,255,255))
        dr = ImageDraw.Draw(im)
        i = 0
        for s in sss:
            #dr.text((10,int(i*(fontc+5)+5)),s['text'],font=setfont,fill=s['color'])
            z = 0
            for k,s2 in enumerate(s['text']):
                #计算坐标
                if s2 == '\n':
                    i = i + 1
                    z = 0
                else:
                    x = int(i*(fontc+5)+5)
                    y = int(z*(fontc+5)+10)
                    s2 = s2.replace('【','︻')
                    s2 = s2.replace('】','︼')
                    s2 = s2.replace('→','↓')
                    s2 = s2.replace('（','︵')
                    s2 = s2.replace('）','︶')
                    dr.text((x,y),s2,font=setfont,fill=s['color'])
                    z = z + 1          
            #制作并粘贴时间的图片
            if s['time'] != None:
                x = int(i*(fontc+5)+5)
                y = int(z*(fontc+5)+10)
                tim = Image.new('RGB',(260,18),(255,255,255))
                tdr = ImageDraw.Draw(tim)
                tdr.text((1,1),s['time'],font=setfont,fill=s['color'])
                #tim.show()
                tt = tim.transpose(Image.ROTATE_270)
                #tim.show()
                im.paste(tt,(x,y))
                tim.close()

            i = i + 1
        name = f'{Mpath}\\pic\\{str(int(time.time()*1000))}.png'
        #im.show()
        im.save(name)
        return name

    def GETLinePIC(self,Line,m=0):
        '''获取线路状态图片'''
        '''m = 1表示竖向'''
        lines,linens = self.GetGuid(str(Line))
        #print('线路GUID',lines)
        picl=[]
        i = 0
        for l in lines:
            while True:   #一直处理获取验证码错误自动重试，当网络错误和其他错误时跳出
                code = self.OCRCOde(self.GetCode(l))
                print('验证码识别：',code)
                if code != None:
                    json = self.GetLineStatus(l,code)
                    #print('获取线路状态json：',json)
                    if json:
                        StandInfo = json.get('StandInfo')
                        if StandInfo != None:
                            sss,Maxssl,H = self.loadLineStatus(json,linens[i])
                            if sss and Maxssl and H:
                                print('模式',m)
                                if m == 1:
                                    print('横向制图')
                                    picl.append(self.MakePic_(sss,Maxssl,H))
                                else:
                                    picl.append(self.MakePic(sss,Maxssl,H))
                                break
                        elif json.get('retCode') == '1':
                            print('验证码识别错误')
                        elif json.get('param') == {}:
                            print('出现问题，重试！')
                        else:
                            print('发生其他错误：',json)
                            break
                    else:
                        print('线路状态获取错误')
                        break
                else:
                    print('验证码识别错误')
            i = i + 1
        return picl

    def pastepic(self,picname:list,m=0):
        '''m = 1表示竖向拼接'''
        picl=[]
        pich=[]
        picw=[]
        w=0
        h=0
        for pic in picname:
            c = Image.open(pic)
            picl.append(c)
            pich.append(c.height)
            picw.append(c.width)
            w=w+c.width
            h=h+c.height
        pich.sort(reverse=True)
        picw.sort(reverse=True)
        #print(pich,picw,w,h)
        if m == 1:
            im = Image.new('RGB',(picw[0],h),(255,255,255))
        else:
            im = Image.new('RGB',(w,pich[0]),(255,255,255))
        i = 0
        for pic in picl:
            if m == 1:
                im.paste(pic,(0,i))
                i = i + pic.height
            else:
                im.paste(pic,(i,0))
                i = i + pic.width
        ln = f'{Mpath}\\pic\\{str(int(time.time()*1000))}000.png'
        im.save(ln)
        return ln

bus:szbus

def on_GroupMessage(Message: MsgChain, sender: GroupInfo):
    if Message.GetCQ().startswith('./'):
        try:
            s = Message.GetCQ().split('/')
            if s[0] == '.' and len(s) >= 2 and is_number(s[1]):
                line = int(s[1])
                try:
                    m = s[2]
                except:
                    m = 0
                ll = bus.GETLinePIC(str(line),int(m))
                l = None
                if len(ll) > 1:
                    l = bus.pastepic(ll,int(m))
                elif len(ll) == 1:
                    l = ll[0]                                    
                if l:
                    Send['sendGroupMsg'](sender.GroupId,MsgChain().joinImg(Path=l))
                else:
                    Send['sendGroupMsg'](sender.GroupId,MsgChain().joinPlain('查询失败！'))
        except:
            ERROR('公交查询异常！')

def Main(sendGroupMsg, SendFriendMsg):
    # 此函数是在主线程以线程的方式被启用，无需返回任何内容
    # 将发送群消息和私聊消息的回调写入dict
    Send['sendGroupMsg'] = sendGroupMsg
    Send['SendFriendMsg'] = SendFriendMsg
    global bus
    bus = szbus()