import requests
def getsec_uid():
    uil = input('抖音个人主页分享出来的链接(如果有汉字删除):')
    print(uil)
    r = requests.get(uil,allow_redirects=False,headers={'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'})
    sec_uid = None
    print(r.status_code)
    print(r.headers)
    if r.status_code == 302:
        location = r.headers['location']
        ls = location.split('?')
        if len(ls) == 2:
            l = ls[1]
            ll = l.split('&')
            for l in ll:
                if l.startswith('sec_uid='):
                    sec_uid = l.replace('sec_uid=','')
                    break
    
    if sec_uid:
        input(sec_uid)
    else:
        input('未查询到')
    return sec_uid