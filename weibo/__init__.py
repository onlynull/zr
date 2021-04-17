from .weibo import *
'''
版本：V 1.0
源码由师兄熬夜赞助
配置文件解释：
    { 
    "weibo": [                                                                                         监听对象列表
        {
        "name": "onlynull",                                                                            用户昵称
        "weiboID": "1076035279542941",                                                                 微博ID，这里的ID不是微博UID。你需要通过UID获取containerid；可以使用同目录下的GETweiboID.py查
        "weiboURL": "https://m.weibo.cn/api/container/getIndex?containerid=1076035279542941",          地址
        "group": [928275029],                                                                          群列表
        "at": true                                                                                     是否@全体
        },
        {
        "name": "onlynull",
        "weiboID": "1076035279542941",
        "weiboURL": "https://m.weibo.cn/api/container/getIndex?containerid=1076035279542941",
        "group": [928275029],
        "at": true
        }
    ]
    }
'''