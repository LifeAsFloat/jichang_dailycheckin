import requests, json, re, os, time

session = requests.session()
# 配置用户名（一般是邮箱）
# email = os.environ.get('EMAIL')
# 配置用户名对应的密码 和上面的email对应上
# passwd = os.environ.get('PASSWD')
# 从设置的环境变量中的Variables多个邮箱和密码 ,分割
emails = os.environ.get('EMAIL', '').split(',')
passwords = os.environ.get('PASSWD', '').split(',')
 
# server酱
SCKEY = os.environ.get('SCKEY')
# PUSHPLUS
Token = os.environ.get('TOKEN')
def push(content):
    if SCKEY != '1':
        url = "https://sctapi.ftqq.com/{}.send?title={}&desp={}".format(SCKEY, 'ikuuu签到', content)
        requests.post(url)
        print('推送完成')
    elif Token != '1':
        headers = {'Content-Type': 'application/json'}
        qq_payload = {"token": Token, 'title': 'ikuuu签到', 'content': content, "template": "json"}
        resp = requests.post(f'http://www.pushplus.plus/send', json=qq_payload, headers=headers).json()
        print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')
    else:
        tim = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        headers = {'Content-Type': 'application/json'}
        qq_payload = {"user_id": "156402944", "message": [{"type": "text", "data": {"text": tim + ":ikuuu" + content}}]}
        # resp = requests.post(f'https://qq.czys.xn--6qq986b3xl/send_private_msg', json=qq_payload, headers=headers).json()
        # print('QQ推送成功' if resp['status'] == 'ok' else 'QQ推送失败')
        # print(resp)
        # print('未使用消息推送推送！')
        # 1. 先发起请求，不加 .json()
        url = 'https://qq.czys.xn--6qq986b3xl/send_private_msg?access_token=qwerqwer'
        resp = requests.post(url, json=qq_payload, headers=headers)

        # 2. 打印关键调试信息
        print(f"【调试信息】状态码: {resp.status_code}")
        print(f"【调试信息】返回内容: {resp.text}")  # 这里会显示服务器到底吐出了什么

        # 3. 尝试解析，如果不通则抛出异常
        try:
            resp_json = resp.json()
        except Exception:
            print("【调试结论】服务器返回的不是JSON，可能是IP被墙或参数错误。")
            # 为了让脚本不报错退出，可以给个空字典或者 pass
            resp_json = {}

# 会不定时更新域名，记得Sync fork

login_url = 'https://ikuuu.boo/auth/login'
check_url = 'https://ikuuu.boo/user/checkin'
info_url = 'https://ikuuu.boo/user/profile'

header = {
        'origin': 'https://ikuuu.boo',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

for email, passwd in zip(emails, passwords):
    session = requests.session()
    data = {
        'email': email,
        'passwd': passwd
    }
    try:
        print(f'[{email}] 进行登录...')
        response = json.loads(session.post(url=login_url,headers=header,data=data).text)
        print(response['msg'])
        # 获取账号名称
        # info_html = session.get(url=info_url,headers=header).text
        # info = "".join(re.findall('<span class="user-name text-bold-600">(.*?)</span>', info_html, re.S))
        # 进行签到
        result = json.loads(session.post(url=check_url,headers=header).text)
        print(result['msg'])
        content = result['msg']
        # 进行推送
        push(content)
    except:
        content = '签到失败'
        print(content)
        push(content)
