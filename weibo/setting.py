# -*- coding: utf-8 -*-
from fractions import Fraction
import requests
import json
import urllib3
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 打开json文件
try:
    fb = open(os.path.dirname(os.path.realpath(__file__)) + '\ini.json', 'rb')
    data = json.load(fb)
    fb.close()
except:
    print('weibo初始化时读入配置文件发生异常，检查配置文件是否填写正常！')

# ----------------------qq群设置----------------------

# qq群id
def groupid(index):
    return data['weibo'][index]['group']
def groupAt(index):
    return data['weibo'][index]['at']

# --------------------------------------------------------
# ----------------------微博设置----------------------
# 手机网页版微博地址


def weibo_url(index):
    weibo_url = data['weibo'][index]['weiboURL']
    return str(weibo_url)

# weibo container id


def weibo_id(index):
    weibo_id = data['weibo'][index]['weiboID']
    return int(weibo_id)


def getName(index):
    name = data['weibo'][index]['name']
    return name

# --------------------------------------------------------

# ---------------------长网址转短网址----------------------------


def get_short_url(long_url_str):
    url = 'http://api.t.sina.com.cn/short_url/shorten.json?source=3271760578&url_long=' + \
        str(long_url_str)
    response = requests.get(
        url,
        verify=False
    ).json()
    # print(response)
    return response[0]['url_short']

# -------------------------------------------------------
