import re
import traceback

import pymysql
import requests
from bs4 import BeautifulSoup

__author__ = 'Evan Yin'

# 爬取各个环保局行政处罚信息

DB = pymysql.connect("localhost", "root", "1234.abcd", "bi")
CUR = DB.cursor()
CUR.execute('''
select firm_name, "本身" as relation from bi.webpage_info
union 
select gudong, "股东" as relation from bi.gudong_info
union 
select name, "分支机构" as relation from bi.fenzhijigou_info
union
select touzi_firm_name, "被投资企业" as relation from bi.touzi_info
''')

records = CUR.fetchall()


def tianjinhuanbaoju():
    for firm in records:
        try:
            resp = requests.get(
                'http://hjbh.tj.gov.cn/govsearch/search.jsp?sword={0}&lastsword=&secondsearch=0&page=1&submit='.format(
                    firm[0]))
            soup = BeautifulSoup(resp.text, 'lxml')
            cnt = int(re.findall(re.compile('(\d*)条'), soup.find('div', class_='tiaojian').text)[0])
            if cnt > 0:
                # print(firm[0], str(cnt))
                uls = soup.find_all('ul', class_='ul_Result')
                for ul in uls:
                    title = ul.find('a').text
                    if '罚' in title:
                        print(title, ul.find('a').attrs['href'])
        except:
            # print(traceback.format_exc())
            print('查询错误: ' + firm[0])
            print()


def hebeihuanbaoju():
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
        'cookie': 'JSESSIONID=44A9C2D70F74EA6196B9831E45967C52; __FT10000005=2019-2-25-10-33-51; __NRU10000005=1551062031564; UM_distinctid=16922805d0113-084c0fdd9fa1b1-675c772b-144000-16922805d03219; __REC10000005=1; __RT10000005=2019-2-27-15-56-54; CNZZDATA1275921890=968511557-1551058607-%7C1551259798; yunsuo_session_verify=26684bbae2343b0d9b666d64195647e2'
    }
    for firm in records:
        data = {
            'channelid': 290895,
            'searchword': "doctitle = '{0}' or doccontent = '{1}'".format(firm[0], firm[0]),
            'LoginName2222': '天津市政投资有限公司',
            'x': 0,
            'y': 0
        }
        try:
            resp = requests.post(
                'http://hbepb.hebei.gov.cn/was5/web/search', data=data, headers=header)
            soup = BeautifulSoup(resp.text, 'lxml')
            if '很抱歉' in soup.find('td', class_='searchresult').text:
                print('没有找到匹配结果')
                continue

            cnt = int(re.findall(re.compile('找到相关结果约(\d*)条'), soup.find('div', class_='outline').text)[0])
            if cnt > 0:
                # print(firm[0], str(cnt))
                tds = soup.find('td', class_='searchresult').find_all('li')
                for li in tds:
                    title = li.find('a').text
                    if '行政处罚' in title:
                        print(title, li.find('a').attrs['href'])
        except:
            print(traceback.format_exc())
            print('查询错误: ' + firm[0])
            print()
# http://www.hebhb.gov.cn/hjzw/zhzf/hjzfbgt/201805/t20180523_63358.html
# http://www.hebhb.gov.cn/hjzw/zhzf/hjzfbgt/201805/t20180523_63356.html
# http://www.hebhb.gov.cn/root8/auto454/201805/t20180515_63124.html
# http://www.hebhb.gov.cn/root8/auto454/201805/t20180515_63123.html
# http://www.hb12369.net/wap/zxfw/spgs/201807/t20180704_64816.html
# http://www.hebhb.gov.cn/hjzw/zhzf/hjzfbgt/201805/t20180523_63384.html
# http://www.hebhb.gov.cn/root8/auto454/201805/t20180515_63090.html
# http://www.hebhb.gov.cn/hjzw/zhzf/hjzfbgt/201805/t20180523_63341.html
# http://www.hebhb.gov.cn/root8/auto454/201805/t20180515_63112.html
# http://www.hebhb.gov.cn/cjhd/xzcf/201801/t20180118_60374.html
# def shanxihuanbao():


hebeihuanbaoju()
DB.close()
