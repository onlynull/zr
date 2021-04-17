from BILI.bilibili import *
'''
版本：V 1.1
使用说明：
        ！！！不要使用windows自带的文档编辑器打开填写！！！
        每个用户的配置里至少需要填写uid和推送群。
        delay 为每个轮询之间的间隔
        forward_draw 为true时表示不屏蔽用户的转发抽奖动态

          {
        "uid": 15272008,                必填 用户ID
        "roomid": 2458117,              用户roomid
        "uname": "onlynull",            用户昵称
        "showname": "汪酱",             有消息推送时在群里暂时的昵称
        "Startvideo": true,             是否启动视频监听
        "StartLive": true,              是否启动开播监听  （你也可以选择关闭此功能，使用LiveBILI模块进行快速推送）
        "StartDynamic": true,           是否开启动态监听  （如果开启动态监听，建议视频监听不用开启，动态监听这里也会监听到作者发布的视频）
        "Group": [                      多个群，复制多个对象到这个数组
        {
                "id": 928275029,        群ID
                "ATall": true,          是否 @全体成员 ，此功能需要机器人为群管理
                "sendPic": true,        发送消息时是否发送图片
                "sendUrl": true         发送消息时是否携带url，例如开播推送会携带直播间url，动态推送会携带动态地址
        },
        {
                "id": 928275029,
                "ATall": true,
                "sendPic": true,
                "sendUrl": true
        }
        ]
        },
'''