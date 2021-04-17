import requests,json,time,os
from msgType import MsgChain,GroupInfo
from PIL import Image, ImageDraw, ImageFont
from Log import INFO,ERROR

__all__ = (
    'Main',  # 此方法不可以注释，否则本模块将不会被添加进任务
    'on_GroupMessage',  # 不需要接收群消息时将此行注释既可
    #'on_FriendMessage'  # 不需要接收私聊消息时将此行注释既可
)

# 用来存放发送消息回调，也可以通过其他方法保存
Send = {'sendGroupMsg': None, 'SendFriendMsg': None}

#当前模块路径
Mpath = os.path.dirname(os.path.realpath(__file__))

url='https://api6.meishichina.com/api.php?p='

_MAPPING = (u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九',
            u'十', u'十一', u'十二', u'十三', u'十四', u'十五', u'十六', u'十七', u'十八', u'十九')
_P0 = (u'', u'十', u'百', u'千',)
_S4 = 10 ** 4

def num_to_chinese4(num):
    assert (0 <= num and num < _S4)
    if num < 20:
        return _MAPPING[num]
    else:
        lst = []
        while num >= 10:
            lst.append(num % 10)
            num = num / 10
        lst.append(num)
        c = len(lst)  # 位数
        result = u''

        for idx, val in enumerate(lst):
            val = int(val)
            if val != 0:
                result += _P0[idx] + _MAPPING[val]
                if idx < c - 1 and lst[idx + 1] == 0:
                    result += u'零'
        return result[::-1]

def Getname(name:str):
    data={
    "m": {
        "search_mobileHotSearch": {
            "keyword": name,
            "pageindex": 1,
            "pagesize": 10,
            "type": "recipe"
        }
    },
    "openudid": "be4ee82d777907c991899a69fa69cdf9",
    "uid": "",
    "appver": "6202",
    "imei": "863254584820715",
    "province": "",
    "city": "",
    "device": "Android+MI+9",
    "appname": "msc_android"
    }
    j = requests.get(url+json.dumps(data)).json()
    if j :
        title=[]
        for d in j['search_mobileHotSearch']['data']:
            s=d['title']+'-['+d['id']+']'
            title.append(s)
        a=[f'搜索到以下{len(title)}个食谱，发送我想',f'吃+食谱后面[]内的数字既可查',f'看详细信息；例如你可以发送：',f'我想吃'+j['search_mobileHotSearch']['data'][0]['id']]
        return a+title
    else:
        return ['未搜索到任何食谱，换一个关键词再试试吧！']

def Getfangfa(id):
    data={
    "m": {
        "recipe_getRecipeInfo": {
            "id": str(id)
        }
    },
    "openudid": "be4ee82d777907c991899a69fa69cdf9",
    "uid": "",
    "appver": "6202",
    "imei": "863254584820715",
    "province": "",
    "city": "",
    "device": "Android+MI+9",
    "appname": "msc_android"
        }
    j = requests.get(url+json.dumps(data)).json()
    if j :
        title=[]
        data=j['recipe_getRecipeInfo']['data']
        title.append(data['title'])
        if data.get('mainingredient','') != '':
            title.append('所需材料：'+data['mainingredient'])
        if data.get('tips','') != '':
            title.append('小提示：'+data['tips'])
        #获取材料相信信息
        ingredient=[]
        for ingredient_groups in data['ingredientgroups']['ingredient_groups']:
            for key in ingredient_groups.get('ingredient',{}):
                ingredient.append(key+'=>'+ingredient_groups['ingredient'][key])
        title.append('、'.join(ingredient))
        i=0
        for steps in data['steps']:
            i=i+1
            title.append(num_to_chinese4(i)+'：'+steps['note'])
        return '\n'.join(title)
    else:
        return ''

def 合成图片(s):
    '''传入字符串数组'''
    ss='\n'.join(s)
    fontc = 20
    setfont = ImageFont.truetype(Mpath+'\\fz.ttf',fontc)
    #计算画布尺寸
    w=0
    H=0
    for sss in s:
        www,hhh = setfont.getsize(sss)
        H=H+hhh
        if www>w:
            w=www
    im = Image.new('RGB',(w,(len(s)+2)*fontc),(255,255,255))
    dr = ImageDraw.Draw(im)
    dr.text((0,0),ss,font=setfont,fill='#000000')
    name = f'{Mpath}\\pic\\{str(int(time.time()*1000))}.png'
    im.save(name)
    return name

def 搜索Food(name:str):
    if name.isnumeric():
        return Getfangfa(name)
    else:
        return Getname(name)

def on_GroupMessage(Message: MsgChain, sender: GroupInfo):
    if Message.GetCQ().startswith('我想吃'):
        try:
            INFO('出现食谱查询指令：'+Message.GetCQ())
            name =  Message.GetCQ()[3:]
            if name.isnumeric():
                Send['sendGroupMsg'](sender.GroupId,MsgChain().joinPlain(Getfangfa(name)))
            else:
                Send['sendGroupMsg'](sender.GroupId,MsgChain().joinImg(Path=合成图片(Getname(name))))
        except:
            ERROR('食谱查询异常')

def Main(sendGroupMsg, SendFriendMsg):
    # 此函数是在主线程以线程的方式被启用，无需返回任何内容
    # 将发送群消息和私聊消息的回调写入dict
    Send['sendGroupMsg'] = sendGroupMsg
    Send['SendFriendMsg'] = SendFriendMsg