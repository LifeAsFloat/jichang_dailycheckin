import requests, json, re, os, time
from datetime import datetime
from zoneinfo import ZoneInfo
import random

# 【修改1】改为从环境变量获取 COOKIES，多个账号使用 ---- 分隔
raw_cookies = os.environ.get('COOKIES', '')
cookies_list = [c.strip() for c in raw_cookies.split('----') if c.strip()]
 
# server酱
SCKEY = os.environ.get('SCKEY')
# PUSHPLUS
Token = os.environ.get('TOKEN')
QQToken = os.environ.get('QQTOKEN')
QQ = os.environ.get('QQ')

# 推送逻辑保持不变
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
        tim = datetime.now(cn_tz).strftime('%Y-%m-%d %H:%M:%S')
        headers = {'Content-Type': 'application/json'}
        qq_payload = {"user_id": QQ, "message": [{"type": "text", "data": {"text": tim + ":ikuuu" + content}}]}
        
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
            print(f"【调试信息】状态码: {resp.status_code}")
            print(f"【调试信息】返回内容: {resp.text}")  
            
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
            try:
                resp = requests.post(moepush_url, json=moepush_payload, headers=moepush_headers, timeout=15)
                print(f"【调试信息】MOEPUSH状态码: {resp.status_code}")
                if resp.status_code == 200:
                    print("【调试信息】MOEPUSH推送成功")
            except Exception as e:
                    print(f"【调试信息】cloudscraper 请求失败: {str(e)}")
                    resp = None       
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
# 【修改2】不再需要 login_url，直接请求 check_url
check_url = 'https://ikuuu.nl/user/checkin'

# 基础请求头
header = {
        'origin': 'https://ikuuu.nl',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'cache-control': 'no-cache',
        'pragma': 'no-cache'
}

if not cookies_list:
    print("❌ 未获取到 COOKIES，请检查环境变量配置。")
    exit(1)

# 【修改3】遍历 Cookie 列表进行签到
for index, cookie in enumerate(cookies_list):
    account_name = f"账号 {index + 1}"
    print(f'\n[{account_name}] 开始签到...')
    
    # 每次循环复制一份 Header，并放入当前账号的 Cookie
    current_headers = header.copy()
    current_headers['cookie'] = cookie
    
    try:
        # 直接发起签到请求
        response = requests.post(url=check_url, headers=current_headers, timeout=10)
        
        # 解析返回结果
        try:
            result = response.json()
            msg = result.get('msg', '签到成功 (未返回具体msg)')
            content = f"{account_name}: {msg}"
            print(content)
            
            # 进行推送
            push(content)
            
        except json.JSONDecodeError:
            # 如果 Cookie 失效，面板通常会重定向到登录页(HTML)，导致 JSON 解析失败
            content = f"{account_name}: 签到失败，Cookie可能已过期或被防火墙拦截"
            print(content)
            push(content)
            
    except Exception as e:
        content = f'{account_name}: 请求报错 - {str(e)}'
        print(content)
        push(content)
    
    # 【优化】如果是多账号，每次签到后随机暂停 2~5 秒，防止并发过高被封 IP
    if index < len(cookies_list) - 1:
        sleep_time = random.randint(2, 5)
        print(f"等待 {sleep_time} 秒后处理下一个账号...")
        time.sleep(sleep_time)
