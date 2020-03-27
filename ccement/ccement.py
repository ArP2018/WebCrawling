#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: loricheung
import time
from collections import namedtuple
from datetime import datetime
import requests
from pymongo import MongoClient
import jsonpath_rw_ext as jp
import pandas as pd


HEADERS = {
    'accept': "application/json, text/javascript, */*; q=0.01",
    'accept-language': "zh-CN,zh;q=0.9",
    # 'cookie': 'acw_tc=71606d1815774174262706297e7d89b60f180b3bfbf68e75587b8cf429; PHPSESSID=g4bq754qhl02qqpof5kfh9m2os; _utmb=5E62F175-4E45-48B5-967C-22E7533634F8; _bl_uid=5gkCa459n37l3ml3yxma1q00pwXm; UM_distinctid=16f4567cba26c-0dffd6f1286f53-6701b35-100200-16f4567cba326f; CNZZDATA1277953252=235721190-1577417418-%7C1577417418; 53gid2=11266366811002; 53gid0=11266366811002; 53gid1=11266366811002; 53revisit=1577417428605; 53kf_72104391_from_host=price.ccement.com; 53kf_72104391_land_page=https%253A%252F%252Fprice.ccement.com%252FPrice_list-127-s20190101-e20190301-p330000-c0-k0-b0.html; kf_72104391_land_page_ok=1; 53uvid=1; onliner_zdfq72104391=0; Hm_lvt_7527936a18d0303cd196c7290698b583=1577417577; Hm_lpvt_7527936a18d0303cd196c7290698b583=1577417577; pc_token=65364da1796f52f2fbb30a38a36a59e5e34f85c15fc46cc756e7541d5a3ebc4d6cf9860ccce0a8cdf3c7d9a63c4c280f010724f5; __lv__=AQoMdHUKDXdrB3IHdmsBB3EGaXNydwAdcwAFc3UDDHUHA3MBSDJHQy8/rIaN0qmj04GpTUhOCnJ3AU3XhvXQvdam4JvQpa7ZrL/QqpbUifCgh5TXqM/cqdGmwZ7Su4hMB0VJAgIECnN/AwAIDDoEAXd3cAQEBQMEBg4ACQ0CCXRiBQAHAjrdkc2lx7fetKpMBgoGAQMBAXFwBAEBBHYFAHFzOARL0qme3rmv1Yio3NXeSAACBn4BBXZ1dAIHBAAABwkFAQ==; __cv__=eDKLn39D9iDv6XhCOsMS0A==; __lt__=116446313417589000; _currentUserName=trsn; Hm_lvt_dfbfaed43eb5a507dc8b019717aeabb7=1577417428,1577417591; visitor_type=old; 53kf_72104391_keyword=https%3A%2F%2Fi.ccement.com%2Fpc%2Flogin.html%3Frefurl%3Dhttps%3A%2F%2Fprice.ccement.com%2FPrice_list-127-s20190101-e20190301-p330000-c0-k0-b0.html; Hm_lpvt_dfbfaed43eb5a507dc8b019717aeabb7=1577417625',
    'cookie':'UM_distinctid=16ef400ccda167-0c2afba79f60d6-675c772b-144000-16ef400ccdb20b; acw_tc=b7e89f2315760519852071796eabfb8099054df3c75635d27b2e3faefc; _bl_uid=skkOe4k517k06Xn8FrR0iUed4U4g; 53gid2=10995418699007; 53revisit=1576051986929; _utmb=261835C0-899A-4309-B34A-CFFB1EAB7F4A; Hm_lvt_7527936a18d0303cd196c7290698b583=1576051728,1577685679; visitor_type=old; 53kf_72104391_from_host=price.ccement.com; 53kf_72104391_land_page=https%253A%252F%252Fprice.ccement.com%252F; kf_72104391_land_page_ok=1; 53uvid=1; onliner_zdfq72104391=0; invite_53kf_totalnum_4=2; PHPSESSID=g15i6a3kf1nf29a6qdh36p09fc; CNZZDATA1277953252=1773672717-1576049978-null%7C1578273530; 53gid0=10995418699007; 53gid1=10995418699007; Hm_lpvt_7527936a18d0303cd196c7290698b583=1578275050; pc_token=4ad5729f750eb494231d3b9318ddc5ac71fbf4867cf2c8d6c86f65be7bff11c0c5b1501299673ac7e0cd37e93baeaeba011c18a5; __lv__=AQoMdHUKDXdrB3IHdmsBB3EGaXNydwAdcwAFc3UDDHUHA3MBSDJHQy8/rIaN0qmj04GpTUhOCnJ3AU3XhvXQvdam4JvQpa7ZrL/QqpbUifCgh5TXqM/cqdGmwZ7Su4hMB0VJAgQKDHZ2BgkAADoEAXd3cAQEBQQCAAwFCAICCXRiBQAHAjrdkc2lx7fetKpMBgoGAQMBAXFwBAEBBHYFAHFzOARL0qme3rmv1Yio3NXeSAACBn4BBXZ1dAIHBAAABwkFAQ==; __cv__=eWcQAUA/Tz+Zx/GxpYcC3g==; __lt__=116446314275096000; _currentUserName=trsn; Hm_lvt_dfbfaed43eb5a507dc8b019717aeabb7=1576051986,1577685698,1578275098; 53kf_72104391_keyword=https%3A%2F%2Fi.ccement.com%2Fpc%2Flogin.html%3Frefurl%3Dhttps%3A%2F%2Fprice.ccement.com%2FPrice_list-334-s0-e0-p370000-c0-k0-b0.html; Hm_lpvt_dfbfaed43eb5a507dc8b019717aeabb7=1578275303',
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    'x-requested-with': "XMLHttpRequest",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
}

QUERY = {
    "_t":"0.4108861955968748",
    "from":"pricelist",
    "page":"1",
    "startTime":"20190101",
    "endTime":"20191230",
    "provinceCode":"410000",
    "cityCode":"410100",
    "Kid":"0",
    "bid":"0"
}

Pc = namedtuple('Pc', ['name', 'id', 'cities'])

url = 'https://price.ccement.com/index/ajax/auth'

referer_pattern = 'https://price.ccement.com/Price_list-{page}-s20190101-e20191230-p{province}-c{city}-k0-b0.html'

# coll = MongoClient('127.0.0.1').get_database('ccement').get_collection('sn')


def get_price_from(page, province_code, city_code):
    # 根据不同的页数, 省市的code构造请求
    referer = referer_pattern.format(page=page, province=province_code, city=city_code)
    headers = HEADERS
    headers.update({'referer': referer})
    query = QUERY
    query.update({'page': str(page), "provinceCode": province_code, "cityCode": city_code})
    r = requests.get(url, headers=headers, params=query)
    data = r.json()
    pages, brands, types, provinces, cities, counties, priceComps, times, bulks, sacks, guides = [],[],[],[],[],[],[],[],[],[],[]
    print(data)
    try:
        price_list = jp.match('$..price_list[*]', data)
        # print(price_list)
        for price in price_list:
            pages.append(page)
            brands.append(price['brand'])
            types.append(price['type'])
            provinces.append(price['province'])
            cities.append(price['city'])
            counties.append(price['county'])
            priceComps.append(price['PriceComp'])
            times.append(price['time'])
            bulks.append(price['bulk'])
            sacks.append(price['sack'])
            guides.append(price['guide'])

        tuples = list(zip(pages, brands, types, provinces, cities, counties, priceComps, times, bulks, sacks, guides))
        output_df = pd.DataFrame(tuples, columns=['页数', '品牌', '水泥品种', '省份', '城市', '区域', '生产厂家', '日期', '散装价', '袋装价', '参考价'])
        # trained = pd.DataFrame(tuples,
        #                        columns=['brand', 'type', 'province', 'city', 'county', 'PriceComp', 'date',
        #                                 'start_priceSack', 'end_priceSack', 'bulk', 'sack', '', 'guide'])
        # coll.insert_many(price_list)
        return True, output_df
    except Exception:
        return False, ''


if __name__ == '__main__':
    # 河南许昌
    # 河南郑州
    # 辽宁大连
    # 山东
    # 浙江
    pc1 = Pc('河南', '410000', {'411000': '许昌', '410100': '郑州'})
    pc2 = Pc('辽宁', '210000', {'210200': '大连'})
    pc3 = Pc('山东', '370000', {'0': '山东'})
    pc4 = Pc('浙江', '330000', {'0': '浙江'})

    # pcs = [pc1, pc2, pc3]
    pcs = [pc3,pc4]

    for pc in pcs:
        province = pc.name
        province_code = pc.id
        print('Current province=' + province)

        for city_code, city in pc.cities.items():
            print('Current city=' + city)
            page = 1
            output = pd.DataFrame(columns=['页数', '品牌', '水泥品种', '省份', '城市', '区域', '生产厂家', '日期', '散装价', '袋装价', '参考价'])
            while 1:
                print('page=' + str(page) + ', province_code=' + str(province_code) + ', city_code='+ str(city_code))
                res, cur_output = get_price_from(page, province_code, city_code)
                if not res:
                    break
                # print(cur_output)
                print(output)
                output = pd.concat([cur_output, output], ignore_index=False)
                # output.append(cur_output)
                page += 1
                time.sleep(10)
            output.to_csv('output_' + province + '_' + city + '.txt', sep='\t', index=False)




