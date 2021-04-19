from msgType import MsgChain, GroupInfo, SenderInfo
from Bot_mirai_cq import on_FriendMessage, on_GroupMessage, mirai, cq
from Log import INFO, ERROR
import threading
import yaml,json
import time
from webserver import zr,apichecklogin,checklogin,request

INFO('开始运行...')
#对，这就是记录版本号的地方，你自己不要改乱了(仅表示发行版本)
INFO('版本号：V 1.1')

#用于存放导入成功的模块
tasks = []

def Import_module(modeule: list):
    '''安装列表内的模块'''
    # 导入模块
    # 包名为目录名，模块为文件夹下的__init__.py，启动后会调用执行一次__init__下的Main函数，
    # 如果不存Main函数将不会执行此模块任何方法
    for t in modeule:
        m = __import__(name=t)
        if 'Main' in dir(m):
            INFO('安装模块：' + str(m))
            tasks.append(m)
        else:
            ERROR('模块：' + str(m) + '未找到Main')
            ERROR(dir(m))


def SendGroupMsg(group, Msg: MsgChain):
    bot.SendGroupMsg(group, Msg)

def SendFriendMsg(QQ, Msg: MsgChain):
    bot.sendFriendMsg(QQ, Msg)

@on_GroupMessage
def on_GroupMessage(Message: MsgChain, sender: GroupInfo):
    for task in tasks:
        if 'on_GroupMessage' in dir(task):
            task.on_GroupMessage(Message, sender)

@on_FriendMessage
def on_FriendMessage(Message: MsgChain, sender: SenderInfo):
    for task in tasks:
        if 'on_FriendMessage' in dir(task):
            task.on_FriendMessage(Message, sender)

if __name__ == '__main__':
    # 读配置文件
    try:
        file = open('config.yaml', mode='r', encoding='utf-8')
        config = yaml.load(file, Loader=yaml.FullLoader)
        file.close()
    except:
        ERROR('读入配置文件或解析时发生异常，检查配置文件是否正确。默认路径为当前目录下的config.yaml。如果没有则需要复制文件 _config(将我复制改名为config.yaml).yaml 为 config.yaml')
        input('回车关闭！')
        exit()
    
    # 导入模块
    Import_module(config['modeules'])

    #实例化机器人，实质上，在机器人实例化后就可以调用机器人的接口了
    if config['mirai_api_http']:
        mirai_api_http = config['mirai_api_http_config']
        bot = mirai(authkey = str(mirai_api_http['authKey']), BOTQQ = mirai_api_http['QQ'],
                    HOST = f'http://{mirai_api_http["host"]}:{str(mirai_api_http["port"])}/')
    else:
        cqhttp = config['cqhttp_config']
        bot = cq(access_token = str(cqhttp['access_token']), host = cqhttp['host'], http_port = str(
            cqhttp['http_port']), ws_port = str(cqhttp['ws_port']))

    #注册机器人部分api接口
    #获取群列表
    @zr.route('/api/grouplist',methods=['GET'])
    @apichecklogin
    def getgroups():
        return json.dumps({'code':200,'msg':'','data':bot.groupList()},ensure_ascii=False)

    #获取群配置信息
    @zr.route('/api/groupconfig',methods=['GET'])
    @apichecklogin
    def getgroupconfig():
        groupid = request.values.get('group')
        if groupid:
            return json.dumps({'code':200,'msg':'','data':bot.groupConfig(groupid)},ensure_ascii=False)
        else:
            return json.dumps({'code':500,'msg':'缺少必要参数group','data':{}},ensure_ascii=False)

    #测试，阻塞运行webhttp
    #zr.run(port=80)

    # 机器人初始化完成后将调用所有模块的Main函数,传入发送群消息和私聊消息的回调
    for task in tasks:
        INFO('启动模块：' + str(task))
        #传入api给部分需要api的模块，dict的方式传递
        if 'SetApi' in dir(task): 
            task.SetApi(
                {
                    'mute':bot.mute,
                    'BOTQQ':bot.BOTQQ,
                    'groupConfig':bot.groupConfig
                }
            )
        #启动Main函数
        threading.Thread(target = task.Main, args = (
            bot.SendGroupMsg, bot.SendFriendMsg),name = str(task)).start()

    

    #阻塞运行websocket接收机器人消息，会一直运行
    while bot.run_forever():
        INFO('机器人websocket断开连接，等待15秒后重新连接。')
        time.sleep(15)
    INFO('程序关闭')