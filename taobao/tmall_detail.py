import json
import os
import traceback

import pandas as pd
import random
import time
import proxy_util as util

import requests

# Custom User Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3)",
    "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16C101 MicroMessenger/7.0.3(0x17000321) NetType/4G Language/zh_CN",
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
]
header = {'user-agent': random.choice(user_agents)}

url = 'https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?jsv=2.4.8&appKey=12574478&t={0}&api=mtop.taobao.detail.getdetail&v=6.0&dataType=jsonp&ttid=2017%40taobao_h5_6.6.0&AntiCreep=true&type=jsonp&callback=mtopjsonp2&data={1}'

proxies = util.Proxies("https")
requestUtil = util.RequestUtility()

tags_path = './data/tags.csv'
sales_path = './data/sales.csv'
desc_path = './data/description.csv'

if not os.path.exists(tags_path):
    with open(tags_path, 'a', encoding='utf-8') as f:
        f.write('id,商品名称,天猫标签,标签数量,舆情正负\n')

if not os.path.exists(sales_path):
    with open(sales_path, 'a', encoding='utf-8') as f:
        f.write('id,商品名称,销售价格,月销量,评论量,商品人气值\n')

if not os.path.exists(desc_path):
    with open(desc_path, 'a', encoding='utf-8') as f:
        f.write('id,商品名称,品牌,型号,功效,产地,适用发质,化妆品净含量\n')

df = pd.read_csv('./data/product_id.csv', )
FLAGS = list(df['flag'])

for id, row in df.iterrows():
    try:
        data_id, sku_id, title = str(row['data_id']), str(row[' sku_id']).lstrip(), str(row[' title']).lstrip()
        flag = row['flag']
        if flag == 'Y':
            continue
        parma_t = str(int(time.time() * 1000))
        param_data = requests.utils.quote('{"itemNumId":"%s"}' % data_id)
        while True:
            resp = requestUtil.get(url.format(parma_t, param_data), headers=header, proxies=proxies, )
            if resp.status_code == 200:

                start = resp.text.find('mtopjsonp2(') + len('mtopjsonp2(')
                # mobile_resp_str
                result = json.loads(resp.text[start:-1])

                if '调用成功' in ''.join(result.get('ret')):
                    break

        # 评价标签   # get('type') 1 or -1
        tags = result.get('data').get('rate')
        if tags and tags.get('keywords'):
            tags = tags.get('keywords')
            for t in tags:
                with open(tags_path, 'a', encoding='utf-8') as f:
                    f.write(
                        '{0},{1},{2},{3},{4}\n'.format(data_id, title, t.get('word'), t.get('count'), t.get('type')))

        # 商品描述
        descs = result.get('data').get('props').get('groupProps')
        if descs and descs[0].get('基本信息'):
            brand, xinghao, gongxiao, chandi, fazhi, volume = '', '', '', '', '', ''
            for info in descs[0].get('基本信息'):
                if '品牌' in info.keys():
                    brand = info.get('品牌')
                elif '型号' in info.keys():
                    xinghao = info.get('型号')
                elif '功效' in info.keys():
                    gongxiao = info.get('功效')
                elif '产地' in info.keys():
                    chandi = info.get('产地')
                elif '适用发质' in info.keys():
                    fazhi = info.get('适用发质')
                elif '化妆品净含量' in info.keys():
                    volume = info.get('化妆品净含量')
            with open(desc_path, 'a', encoding='utf-8') as f:
                f.write(
                    '{0},{1},{2},{3},{4},{5},{6},{7}\n'.format(data_id, title, brand, xinghao, gongxiao, chandi, fazhi,
                                                               volume))

        # 商品销售及人气
        fav_count = result.get('data').get('item').get('favcount')

        # 累计评价
        comment_count = result.get('data').get('item').get('commentCount')

        # 价格
        price_set = json.loads(result.get('data').get('apiStack')[0].get('value'), ).get('skuCore').get('sku2info')
        if sku_id in price_set.keys():
            price = price_set.get(sku_id).get('price').get('priceText')
        elif len(price_set) == 1:
            price = price_set.get('0').get('price').get('priceText')
        else:
            price = ''

        # 月销量
        sell_count = json.loads(result.get('data').get('apiStack')[0].get('value')).get('item').get('sellCount')

        with open(sales_path, 'a', encoding='utf-8') as f:
            f.write('{0},{1},{2},{3},{4},{5}\n'.format(data_id, title, price, sell_count, comment_count, fav_count))

        FLAGS[id] = 'Y'

    except:
        print(traceback.format_exc())
        FLAGS[id] = 'N'

df['flag'] = FLAGS
df.to_csv('./data/product_id.csv', index=False)
