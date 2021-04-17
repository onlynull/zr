'''基于mirai api http的简易消息类型'''
'''
def Plain(T):
    return {'type':'Plain','text':T},T

def Image(Path='', ImageId='', Url=''):
    if Path != '':
        return {'type':'Image','path':Path},f'[CQ:image,file=file:///{Path}]'
    elif ImageId != '':
        return {'type':'Image','imageId':ImageId},f'[CQ:image,file={ImageId}]'
    else:
        return {'type':'Image','url':Url},f'[CQ:image,file={Url}]'

def At(QQ):
    加入一个at，当qq为正整数时为at某个人，为非正整数时则为at全体
    if int(QQ) > 0:
        return {'type' :'At', 'target':int(QQ)},f'[CQ:at,qq={str(QQ)}]'
    else:
        return {'type' :'AtAll'},'[CQ:at,qq=all]'

def App(T):
    加入一个App消息，基本上为json文本
    return {'type':'App','content':T},f'[CQ:json,data={T}]'
'''

class SenderInfo:
    Senderid = None
    Sendername = None
    Senderpermission = None
    Senderremark = None

class GroupInfo(SenderInfo):
    GroupId = None
    GroupName = None
    Grouppermission = None        

class MsgChain:
    '''消息链'''
    msg = None
    msgs = ''
    fromType=''     #消息来源类型，仅为接收消息时可用，发送时不用填写
    Quote = None    #引用、回复
    ID = None       #消息ID，仅在收到消息可用
    def __init__(self,Messenger = []) -> None:
        if Messenger != []:
            self.msg = Messenger#这个地方进行赋值，是为了self实例不会与其他实例的msg共用一个
        else: self.msg = []

    def clear(self):
        '''清空消息链'''
        self.msg.clear()

    def joinPlain(self,T:str):
        '''加入一条文本消息'''
        msg = {'type':'Plain','text':T}
        self.msg.append(msg)
        self.msgs = self.msgs + T
        return self

    def joinImg(self,Path=None, ImageId=None, Url=None):
        '''加入一张图片
        mirai api http发送图片时，加入本地图片时如果mirai返回code：6 则会自动上传图片再次发送
        go_cqhttp不支持上传图片，(言外之意就是脚本和gohttp不在一台机器上没法发送脚本所在的本地图片)
        '''
        msg = {'type':'Image','imageId':ImageId,'url':Url,'path':Path}
        self.msg.append(msg)
        if Path != None:
            self.msgs = self.msgs + f'[CQ:image,file=file:///{Path}]'
        elif Url != None:
            self.msgs = self.msgs + f'[CQ:image,file={Url}]'
        else:
            self.msgs = self.msgs + f'[CQ:image,file={ImageId}]'
        return self

    def joinVoice(self,Path=None, VoiceId=None, Url=None):
        '''加入一条语音,通常是单独发送一条语音'''
        msg = {'type':'Voice','voiceId':VoiceId,'url':Url,'path':Path}
        self.msg.append(msg)
        if Path != None:
            self.msgs = self.msgs + f'[CQ:record,file=file:///{Path}]'
        elif Url != None:
            self.msgs = self.msgs + f'[CQ:record,file={Url}]'
        else:
            self.msgs = self.msgs + f'[CQ:record,file={VoiceId}]'
        return self

    def joinVideo(self,Path=None, VideoId=None, Url=None):
        '''
        加入一条短视频,通常是单独发送一条视频
        目前仅GO_CQHTTP支持发送短视频
        '''
        msg = {'type':'Video','videoId':VideoId,'url':Url,'path':Path}
        self.msg.append(msg)
        if Path != None:
            self.msgs = self.msgs + f'[CQ:video,file=file:///{Path}]'
        elif Url != None:
            self.msgs = self.msgs + f'[CQ:video,file={Url}]'
        else:
            self.msgs = self.msgs + f'[CQ:video,file={VideoId}]'
        return self

    def joinAT(self,qq):
        '''加入一个at，当qq为正整数时为at某个人，为非正整数时则为at全体'''
        if int(qq) > 0:
            msg = {'type' :'At', 'target':int(qq)}
            self.msgs = self.msgs + f'[CQ:at,qq={str(qq)}]'
        else:
            msg = {'type' :'AtAll'}
            self.msgs = self.msgs + '[CQ:at,qq=all]'
        self.msg.append(msg)
        return self

    def joinFace(self,faceId):
        '''加入一个QQ表情'''
        msg = {'type':'Face','faceId':faceId}
        self.msg.append(msg)
        self.msgs = self.msgs + f'[CQ:face,id={str(faceId)}]'
        return self

    def joinPoke(self,QQorName):
        '''
        加入一个戳一戳，戳你的沙雕群友吧。
        注意：此方法构造的功能在gohttp和mirai api http上面的实现不一样
            gohttp为你戳某个人的头像产生的效果；mirai_api_http为你发送的窗口抖动产生的效果
            gohttp:QQorName为你要戳的那个人的QQ号
            mirai_api_http:QQorName则为要发送的窗口抖动内容
                "Poke": 戳一戳
                "ShowLove": 比心
                "Like": 点赞
                "Heartbroken": 心碎
                "SixSixSix": 666
                "FangDaZhao": 放大招    
        '''
        msg = {'type':'Poke','name':QQorName}
        self.msg.append(msg)
        self.msgs = self.msgs + f'[CQ:poke,qq={QQorName}]'
        return self

    def joinApp(self,T:str):
        '''加入一个App消息，基本上为json文本'''
        msg = {'type':'App','content':T}
        self.msg.append(msg)
        self.msgs = self.msgs + f'[CQ:json,data={T}]'
        return self
    
    def joinJson(self,T:str):
        '''加入一个App消息，基本上为json文本'''
        msg = {'type':'Json','json':T}
        self.msg.append(msg)
        self.msgs = self.msgs + f'[CQ:json,data={T}]'
        return self

    def joinXml(self,T:str):
        '''加入一个Xml文本'''
        msg = {'type':'Xml','xml':T}
        self.msg.append(msg)
        self.msgs = self.msgs + f'[CQ:xml,data={T}]'
        return self

    def joinQuote(self,id):
        '''添加一条引用、回复。无论调用多少次，都会以最后一次为准'''
        self.Quote = int(id)
        return self

    def __add__(self,other):
        '''此方法用来制定self + other的规则'''
        self.msg = self.msg + other.msg
        self.msgs = self.msgs + other.msgs
        return self

    def GetCQ(self) -> str:
        '''获取酷Q消息格式'''
        return self.msgs

    def AddCQMsg(self,T:str):
        '''添加一条酷Q消息文本,并分析发送者,此方法为从http获取到消息解析使用。正常勿使用此方法！，如果你想直接添加一条CQ消息可以修改成员变量<MsgChain.msgs>为CQ消息格式的文本既可'''
        if T:
            if T.get('message_type') == 'group':
                self.ID = T['message_id']
                self.fromType = 'Group'
                sender_j = T['sender']
                sender = GroupInfo()
                sender.Senderid = sender_j['user_id']
                sender.Sendername = sender_j['card'] if sender_j['card'] else sender_j['nickname']
                sender.Senderpermission = sender_j['role']
                sender.GroupId = T['group_id']
                #sender.GroupName = 
                sender.Grouppermission = sender_j['role']
            elif T.get('message_type') == 'private':
                self.ID = T['message_id']
                self.fromType = 'Friend'
                sender_j = T['sender']
                sender = SenderInfo()
                sender.Senderid = sender_j['user_id']
                sender.Sendername = sender_j['nickname']
                #sender.Senderpermission = sender_j['remark']
            else: return None
            self.msgs = T.get('message')
            return sender

    def AddMraiMsg(self,T):
        '''添加mirai消息格式json文本，并分析发送者,此方法为从http获取到消息解析使用。正常勿使用此方法！'''
        if T:
            if T['type'] == 'GroupMessage':
                self.fromType = 'Group'
                sender_j = T['sender']
                sender = GroupInfo()
                sender.Senderid = sender_j['id']
                sender.Sendername = sender_j['memberName']
                sender.Senderpermission = sender_j['permission']
                sender.GroupId = sender_j['group']['id']
                sender.GroupName = sender_j['group']['name']
                sender.Grouppermission = sender_j['group']['permission']
            elif T['type'] == 'FriendMessage':
                self.fromType = 'Friend'
                sender_j = T['sender']
                sender = SenderInfo()
                sender.Senderid = sender_j['id']
                sender.Sendername = sender_j['nickname']
                sender.Senderpermission = sender_j['remark']
            else: return None
            #置入消息
            for message in T['messageChain']:
                mt = message['type']
                if mt == 'Plain':
                    self.joinPlain(message['text'])
                elif mt == 'At':
                    self.joinAT(message['target'])
                elif mt == 'AtAll':
                    self.joinAT(0)
                elif mt == 'Face':
                    self.joinFace(message['faceId'])
                elif mt == 'Image':
                    self.joinImg(message['path'],message['imageId'],message['url'])
                elif mt == 'FlashImage':
                    self.joinImg(message['path'],message['imageId'],message['url'])
                elif mt == 'Poke':
                    self.joinPoke(message['name'])
                elif mt == 'App':
                    self.joinApp(message['content'])
                elif mt == 'Json':
                    self.joinJson(message['json'])
                elif mt == 'Xml':
                    self.joinXml(message['xml'])
                elif mt == 'Source':
                    self.ID = message['id']
                elif mt == 'Voice':
                    self.joinVoice(message['path'],message['voiceId'],message['url'])
                elif mt == 'Video':
                    self.joinVideo(message['path'],message['voiceId'],message['url'])
            return sender

if __name__ == "__main__":
    input('你开错啦，要运行LoveZR.py。你个憨憨！')