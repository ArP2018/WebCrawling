import time

import pymysql
import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, Firefox

from selenium.webdriver.chrome.options import Options

url = 'http://hd.chinatax.gov.cn/xxk/'
db = pymysql.connect("localhost", "root", "1234.abcd", "bis")
cur = db.cursor()

URL = 'http://www.csrc.gov.cn/wcm/govsearch/gov_list_ad.jsp'
HEADER = {
    'cookie': 'JSESSIONID=29B0AD75FE2DDBCD935B4054946F21BF',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
}

sql = 'select firm_id, firm_name from bis.firm_info'
sql_01 = 'insert into zhengjianhui(firm_id, name) values(%s, %s)'
insert_sql = 'insert into zhengjianhui(firm_id, name, title, url) values(%s, %s, %s, %s)'
cur.execute(sql)
firms = cur.fetchall()
for idx, firm in enumerate(firms):
    DATA = {
        'pubwebsite': '/zjhpublic/',
        'SType': 3,
        'idxId': '',
        'Title': '',
        'SearchOfContent': firm[1],
        'PubDateSel': '',
        'dc1': '',
        'dc2': '',
        'fileNum': '',
        'keyWords': '',
        'SearchClassInfoId': '3274,3537,3275,3276,3277,3280',
        'SearchClassInfoIdMy': 0,
        'dispatchUnit': 0
    }
    print('正在查询: ' + firm[1])
    resp = requests.post(URL, headers=HEADER, data=DATA)
    soup = BeautifulSoup(resp.text, 'lxml')
    for name, url in [(td.find('a').text, 'http://www.csrc.gov.cn' + td.find('a').attrs['href']) for td in
                      soup.find('div', id='documentContainer').find_all('div', class_='row')]:
        print(name, url)
        print('--' * 50)

        cur.execute(insert_sql, (firm[0], firm[1], name, url))
        db.commit()
    cur.execute(sql_01, (firm[0], firm[1]))
    db.commit()

time.sleep(5)
