import requests, json, re, os, time
from datetime import datetime
from zoneinfo import ZoneInfo
import random

try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False

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
QQToken = os.environ.get('QQTOKEN')
QQ = os.environ.get('QQ')

def push(content):
    if SCKEY and SCKEY != '1':
        url = "https://sctapi.ftqq.com/{}.send?title={}&desp={}".format(SCKEY, 'ikuuu签到', content)
        requests.post(url)
        print('推送完成')
    elif Token and Token != '1':
        headers = {'Content-Type': 'application/json'}
        qq_payload = {"token": Token, 'title': 'ikuuu签到', 'content': content, "template": "json"}
        resp = requests.post(f'http://www.pushplus.plus/send', json=qq_payload, headers=headers).json()
        print('push+推送成功' if resp['code'] == 200 else 'push+推送失败')
    else:
        # 指定时区为上海
        cn_tz = ZoneInfo("Asia/Shanghai")
        # 获取该时区的当前时间并格式化
        tim = datetime.now(cn_tz).strftime('%Y-%m-%d %H:%M:%S')
        # tim = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        headers = {'Content-Type': 'application/json'}
        qq_payload = {"user_id": QQ, "message": [{"type": "text", "data": {"text": tim + ":ikuuu" + content}}]}
        # resp = requests.post(f'https://qq.czys.xn--6qq986b3xl/send_private_msg', json=qq_payload, headers=headers).json()
        # print('QQ推送成功' if resp['status'] == 'ok' else 'QQ推送失败')
        # print(resp)
        # print('未使用消息推送推送！')
        # 1. 先发起请求，不加 .json()
        url = f'https://qq.czys.xn--6qq986b3xl/send_private_msg?access_token={QQToken}'
        qq_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive'
        }
        try:
            resp = requests.post(url, json=qq_payload, headers=qq_headers, timeout=10)

            # 2. 打印关键调试信息
            print(f"【调试信息】状态码: {resp.status_code}")
            print(f"【调试信息】返回内容: {resp.text}")  # 这里会显示服务器到底吐出了什么
            
            # 如果是403错误，提示用户检查
            if resp.status_code == 403:
                print("【调试结论】请求被防火墙拦截，请检查API服务是否可用")
        except requests.exceptions.RequestException as e:
            print(f"【调试信息】请求失败: {str(e)}")

        
        moepush_payload = {"time": tim, 'title': 'ikuuu签到', 'content': content}
        moepush_headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        try:
            moepush_url = 'https://mp.czys.xn--6qq986b3xl/api/push-group/LEx4FIBBcJ5lH2o7'
            
            # 尝试使用 cloudscraper 绕过 Cloudflare
            if HAS_CLOUDSCRAPER:
                print("【调试信息】使用 cloudscraper 来处理 Cloudflare 防护...")
                scraper = cloudscraper.create_scraper()
                try:
                    resp = scraper.post(moepush_url, json=moepush_payload, headers=moepush_headers, timeout=15)
                    print(f"【调试信息】MOEPUSH状态码: {resp.status_code}")
                    if resp.status_code == 200:
                        print("【调试信息】MOEPUSH推送成功")
                except Exception as e:
                    print(f"【调试信息】cloudscraper 请求失败: {str(e)}")
                    resp = None
            else:
                # 如果没有 cloudscraper，使用普通请求
                print("【调试提示】未安装 cloudscraper，尝试使用普通请求（可能会被 Cloudflare 拦截）...")
                resp = requests.post(moepush_url, json=moepush_payload, headers=moepush_headers, timeout=15)
                print(f"【调试信息】MOEPUSH状态码: {resp.status_code}")
            
            if resp and resp.status_code == 403:
                print("【调试结论】MOEPUSH 被 Cloudflare 拦截，建议：")
                print("  1. 如果在本地运行，安装 cloudscraper: pip install cloudscraper")
                print("  2. 如果在 GitHub Actions 运行，可能是 IP 被标记，请更换其他推送服务")
                print("  3. 可以忽略此错误，程序会继续运行")
            elif resp and resp.status_code == 200:
                try:
                    resp_json = resp.json()
                    print(f"【调试信息】MOEPUSH 返回: {resp_json}")
                except Exception:
                    print("【调试结论】MOEPUSH 返回非 JSON 格式，但状态码为 200")
        except requests.exceptions.RequestException as e:
            print(f"【调试信息】MOEPUSH 请求异常: {str(e)}")
            print("【调试建议】请检查网络连接或 MOEPUSH 服务是否可用")

# 会不定时更新域名，记得Sync fork

login_url = 'https://ikuuu.nl/auth/login'
check_url = 'https://ikuuu.nl/user/checkin'
info_url = 'https://ikuuu.nl/user/profile'

header = {
        'origin': 'https://ikuuu.nl',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'cache-control': 'no-cache',
        'pragma': 'no-cache'
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
