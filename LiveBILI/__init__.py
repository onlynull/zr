from .Livebili import *
'''
bilibili直播监听专用-websocket
使用方法：配置文件和BILI类似。必须填入roomid
        
        {
        "uid": "15272008",
        "roomid": 2458117,          必填项！
        "name": "",
        "showname": "/bin/cat",     用于向群内推送消息时暂时的名称
        "savegift":true,            保存礼物日志
        "savedanmu":true,           保存弹幕
        "Group": [                  多个群，复制多个对象到这个数组
            {
            "id": 691963133,        需要推送的群ID
            "ATall": false,         是否需要at全体
            "sendPic": true,        是否发送封面，此功能暂时没用
            "sendUrl": true,        是否发送直播间连接
            "roominfo": false       是否发送直播间除了开播信息的其他一些信息
            },
            {
            "id": 691963133,        需要推送的群ID
            "ATall": false,         是否需要at全体
            "sendPic": true,        是否发送封面，此功能暂时没用
            "sendUrl": true,        是否发送直播间连接
            "roominfo": false       是否发送直播间除了开播信息的其他一些信息
            }
        ]
        },
'''