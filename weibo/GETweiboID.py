# -*- coding: utf-8 -*-
import requests

def GETWEIBOID(uid):
    url=f"https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}"
    header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 \
            Safari/537.36'}
    r = requests.get(url, headers=header).json()
    containerid = ''
    for tabs in r['data']['tabsInfo']['tabs']:
        if tabs['tabKey'] == 'weibo':
            containerid = tabs['containerid']
            pass
    return containerid,r['data']['userInfo']['screen_name']

if __name__ == "__main__":
    uid = input('输入微博UID获取containerid，UID：')

    try:
        containerid,name = GETWEIBOID(uid)
        print(f"将containerid填入ini.json文件里对应的博主数据里，containerid：{containerid} 昵称：{name}")
        pass
    except:
        print('获取数据发生异常，检查网络或重试')