import re
import time
import traceback

from bs4 import BeautifulSoup

URL = 'http://www.cbrc.gov.cn/search/search.jsp'
SUB_URL = 'http://www.cbrc.gov.cn/search/search.jsp?page={0}&searchword=DOC_FORMDATE=2000.1.1%20to%202019.2.25%20AND%20DOC_CLOB={1}&agencyShortlink='

header = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'cookie': '__jsluid=933acd90ed965a3a2c7172633348efd5',
    'host': 'www.cbrc.gov.cn',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
}

import requests

import pymysql
import bs4

db = pymysql.connect("localhost", "root", "1234.abcd", "bi")
cur = db.cursor()
cur.execute('select touzi_firm_id, touzi_firm_name, touzi_firm_url from bi.touzi_info')
firms = cur.fetchall()


def parse_chufa(name, soup):
    try:
        lis = [t for t in soup.find('div', id='sousuo').children if isinstance(t, bs4.element.Tag)][2].find_all('li')


        for li in lis:
            lanmu = li.find_all('div')[1]
            if '处罚' not in lanmu.text:
                continue

            title = li.find('a').text
            chufa_url = 'http://www.cbrc.gov.cn' + li.find('a').attrs['href']

            print(name, title, chufa_url)
    except:
        print(traceback.format_exc())
        return


for firm in firms:

    firm_name = firm[1]

    if firm_name == 'CLH 12(HK)Limited':
        continue

    search_word = 'DOC_FORMDATE=2000.1.1 to 2019.2.25 AND DOC_CLOB={0}'.format(firm_name)
    data = {
        'searchword': search_word,
        'agencycode': '',
        'agencyShortlink': '',
        'Title': '',
        'Relation': 'AND',
        'Content': firm_name,
        'dc1': '2000.1.1',
        'dc2': '2019.2.25',
        'sortfield': '-DOC_FORMDATE',
        'sub1': '检索'
    }
    time.sleep(2)
    resp = requests.post(URL, data=data, headers=header)
    soup = BeautifulSoup(resp.content, 'lxml')
    parse_chufa(firm_name, soup)

    page_info = soup.find('font', text=re.compile('\d+ / \d+'))
    if page_info:
        page_count = re.findall(re.compile('\d+ / (\d+)'), page_info.text)[0]
    else:
        page_count = 1

    print('查询主体: {0}, 查询结果 共 {1} 页 '.format(firm_name, page_count))

    for p in range(2, int(page_count) + 1):
        print('开始查询第 {0} 页'.format(str(p)))
        temp_url = SUB_URL.format(p, firm_name)
        time.sleep(2.5)
        resp = requests.get(temp_url)
        soup = BeautifulSoup(resp.content, 'lxml')
        parse_chufa(firm_name, soup)

db.close()
