import json
import time

import requests

wx_url = "https://mp.weixin.qq.com/mp/profile_ext"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat QBCore/3.43.901.400 QQBrowser/9.0.2524.400'
}

def parse_weixin(offset):
    # 构造url请求参数  __biz, uin, key, pass_ticket, appmsg_token这五个参数需要自行修改
    params = {
        'action': 'getmsg',
        '__biz': 'MzIwNDQ4ODExNQ==',
        'f': 'json',
        'offset': str(offset),
        'count': '10',
        'is_ok': "1",
        'scene': '124',
        'uin': 'NDE4MTk5MzIw',
        'key': 'e6e0bf5c3f2e82dbb779636669409f7e56c51030f59eab94876fb95aec78a3b53f23a965e4103fcd17d6ed67ce9d1326f9f02fd3069b93f8f411e940d5b4d75f4636ab8d9eb7e713c2040b73728d61d3',
        'pass_ticket': '4uV0cnaUHfoNAlEOsxepz5/vROPUjHwVNLwy06AwRJ0gw/IB0AHK3W2mG5Cp4uuZ',
        'wxtoken': '',
        'appmsg_token': '999_26iKP%2BshbywGWjnDl4jXTs5PkYp2-Fb-S1TtJA~~',
        'x5': '0'
    }

    res = requests.get(wx_url, headers=headers, params=params)

    data = json.loads(res.text)
    msg_data = json.loads(data['general_msg_list'])
    for msg in msg_data.get('list', []):
        url, title = msg['app_msg_ext_info']['content_url'], msg['app_msg_ext_info']['title']
        print(title, url)
        print('---------------------------------------------------------------------------------')
        # time.sleep(0.2)

        # 爬取文章正文内容
        time.sleep(0.5)
        # resp = requests.get(url, headers=headers)
        # print(resp.text)

    next_offset = data['next_offset']
    can_msg_continue = data['can_msg_continue']

    # 判断是否还可以继续翻页
    if can_msg_continue:
        # time.sleep(1)
        parse_weixin(next_offset)
    else:
        print('爬取完毕！')

parse_weixin(0)
