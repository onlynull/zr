#项目web配置服务插件

from flask import Flask, config, request,session,redirect,send_file
from flask_cors import CORS
import json,functools,os,yaml
path = os.path.dirname(os.path.realpath(__file__))

'''
定义返回Response为json时code含义：
    200：状态正常
    401：未登录
    404：未找到指定项目
    500：操作失败
'''

#实例化对象，zr作为web对象
zr = Flask('zr')
zr.secret_key = '123'
zr.debug=True
CORS(zr, resources=r'/*')

def readconfig():
    try:
        file = open('config1.yaml', mode='r', encoding='utf-8')
        config = yaml.load(file, Loader=yaml.FullLoader)
        file.close()
        return config
    except:
        print('读入配置文件或解析时发生异常，检查配置文件是否正确。默认路径为当前目录下的config.yaml。如果没有则需要复制文件 _config(将我复制改名为config.yaml).yaml 为 config.yaml')
        return {}

#登录
@zr.route('/login',methods=['GET','POST'],endpoint='l1') # endpoint用于url_for
def login():
    if request.method == "GET": # 当get方法访问登录页面,返回登录页面
        token = request.values.get('token')
        if token == 'www123':  # 判断用户,用户信息可以放在数据库内
            session['token'] = token  # 在session中添加登录的用户,在访问其他页面时可以使用
            print(session.get('token'),session)
            return redirect('/')
        return '<h1>login</h1>'
        #return render_template('login.html')
    else: # 当post方法访问时,则进行判断登录验证
        token = request.form.get('token')  # 获得form中name="user"对应的值
        if token == 'www123':  # 判断用户,用户信息可以放在数据库内
            print(token)
            session['token'] = token  # 在session中添加登录的用户,在访问其他页面时可以使用
            print(session.get('token'),session)
            return redirect('/')
        return '密码错误'
        #return render_template('login.html',error='用户名或密码错误')  # 如果登录验证错误,则跳回本页面,并提示


# 验证用户身份的装饰器，这里会重定向
def checklogin(func): 
    @functools.wraps(func) # 作用是保持被装饰函数的函数名,因为url_for是根据函数名来的,如果不保持会报错,或者使用endpoint取别名
    def inner(*args,**kwargs):
        token = session.get('token')
        #print(token,session)
        if not token:
            return redirect("/login")
            #return redirect("/login",302,json.dumps({'code':401,'msg':'未登录，此操作需先验证用户','data':{}},ensure_ascii=False))
        return func(*args,**kwargs)
    return inner

# api端验证用户身份的装饰器，这里不会重定向
def apichecklogin(func): 
    @functools.wraps(func) # 作用是保持被装饰函数的函数名,因为url_for是根据函数名来的,如果不保持会报错,或者使用endpoint取别名
    def inner(*args,**kwargs):
        token = session.get('token')
        #print(token,session)
        if not token:
            return json.dumps({'code':401,'msg':'未登录，此操作需先验证用户','data':{}},ensure_ascii=False)
            #return redirect("/login",302,json.dumps({'code':401,'msg':'未登录，此操作需先验证用户','data':{}},ensure_ascii=False))
        return func(*args,**kwargs)
    return inner

#图标
@zr.route('/favicon.ico',methods=['GET'],endpoint='favicon')
def favicon():
    return send_file('./favicon.ico',mimetype='image/png',as_attachment=False,attachment_filename='favicon.ico')

#主页
@zr.route('/',methods=['GET'],endpoint='index')
@checklogin
def index():
    print(session.get('token'),session)
    return '<h1>Index</h1>'

def getdirs(file_dir):
    '''取指定目录下的文件夹列表，不对文件夹再取子目录'''
    for root, dirs, files in os.walk(file_dir):
        return dirs

def getfile(file):
    for root, dirs, files in os.walk(file):
        return files

#遍历当前目录下的所有模块
def lookup():
    m=[]
    for dir in getdirs(path):
        file = getfile(path+"\\"+dir)
        if '__init__.py' in file:
            m.append(dir)
    return m

#api
#未被定义api的路由
@zr.route('/api/<a>',methods=['GET'])
def other(a):
    print(a)
    return json.dumps({'code':404,'msg':f'Not Found <{a}>','data':{}},ensure_ascii=False)

#列出所有模块
@zr.route('/api/modules',methods=['GET'])
def modules():
    ms=[]
    m = lookup()
    config = readconfig()
    for mm in m:
        if mm in config.get('modeules',[]):
            ms.append({'name':mm,'status':True})
        else:
            ms.append({'name':mm,'status':False})
    #m = ['482021','48tools','douyin','cookbook','szbus','48','BILI','Acfun','music','Imgbot','LiveBILI','weibo','一言','demo']
    return json.dumps({'code':200,'msg':'读取配置文件失败，仅列出所有模块，是否使用未知' if config == {} else '','data':ms},ensure_ascii=False)

#获取机器人配置信息，需要登录
@zr.route('/api/botconfig',methods=['GET'])
@apichecklogin
def getbotconfig():
    config = readconfig()
    return json.dumps({'code':200 if config else 500,'msg':'读取配置文件失败，检查目录下是否存在配置文件。读入配置文件或解析时发生异常，检查配置文件是否正确。默认路径为当前目录下的config.yaml。如果没有则需要复制文件 _config(将我复制改名为config.yaml).yaml 为 config.yaml' if config == {} else '','data':config},ensure_ascii=False)

#设置机器人配置，需要登录
@zr.route('/api/botconfig',methods=['POST'])
@apichecklogin
def setbotconfig():
    try:
        code = 200
        msg=''
        j = json.loads(request.get_data())
        #检查传回的值
        #检查必填项
        if j.get('mirai_api_http'):
            c = j.get('mirai_api_http_config')
            if c:
                if c['QQ'] and c['authKey'] and c['host'] and c['port']:                    
                    pass
                else:
                    code = 500
                    msg='mirai_api_http_config 缺少配置'
            else:
                code = 500
                msg='未配置 mirai_api_http_config'
        elif j.get('cqhttp'):
            c = j.get('cqhttp_config')
            if c:
                if c['access_token'] and c['ws_port'] and c['host'] and c['http_port']: 
                    pass
                else:
                    code = 500
                    msg='cqhttp_config 缺少配置'
            else:
                code = 500
                msg = '未配置 cqhttp_config'
        else:
            code = 500
            msg = '未选择启用的机器人类型'
        if code == 500:
            return json.dumps({'code':code,'msg':msg,'data':{}},ensure_ascii=False)
        file = open('config1.yaml', mode='w', encoding='utf-8')
        yaml.dump(j,file)
        file.close()
        return json.dumps({'code':200,'msg':'写入成功','data':{}},ensure_ascii=False)
    except:
        print('setbotconfig-写入配置文件失败')
        return json.dumps({'code':500,'msg':'写入失败','data':{}},ensure_ascii=False)


if __name__ == '__main__':
    #print(lookup())
    zr.run(port=80)