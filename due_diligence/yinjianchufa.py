import datetime
import re
import time
import traceback

import pymysql
from bs4 import BeautifulSoup

__author__ = 'Evan Yin'

# 银监会处罚 (银监会机关)
# http://www.cbrc.gov.cn/chinese/home/docViewPage/110002.html
# (银监局)
# http://www.cbrc.gov.cn/zhuanti/xzcf/get2and3LevelXZCFDocListDividePage//1.html
# (银监分局)
# http://www.cbrc.gov.cn/zhuanti/xzcf/get2and3LevelXZCFDocListDividePage//2.html

import requests

JIGUAN_URL = 'http://www.cbrc.gov.cn/chinese/home/docViewPage/110002&current={0}'
YINJIANJU_URL = 'http://www.cbrc.gov.cn/zhuanti/xzcf/get2and3LevelXZCFDocListDividePage//1.html?current={0}'
FENJU_URL = 'http://www.cbrc.gov.cn/zhuanti/xzcf/get2and3LevelXZCFDocListDividePage//2.html?current={0}'
# BAOJIANJU_URL = 'http://bxjg.circ.gov.cn/web/site0/tab5241/module14458/page{0}.htm'
DB = pymysql.connect("localhost", "root", "1234.abcd", "bi")
CUR = DB.cursor()
SQL = 'insert into yinjianchufa(title, url, source, wenshuhao, chufageren, chufadanwei, danweifaren, weiguineirong,chufayiju, chufajieguo, chufajiguan, chufariqi,crawl_id, crawl_date) values(%s, %s, %s,%s, %s, %s,%s,%s, %s, %s,%s, %s, %s,%s)'
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
}

CRAWL_ID = 111


def parse_yinjianhui(soup: BeautifulSoup):
    for td in soup.find('table', id='testUI').find_all('td', class_='cc')[:-1]:
        a = td.find('a')
        title = a.attrs['title']
        url = 'http://www.cbrc.gov.cn' + a.attrs['href']
        source = '中国银监会网站'
        try:
            time.sleep(0.5)
            resp = requests.get(url, headers=header)
            detial_soup = BeautifulSoup(re.findall(re.compile('(<body[^>]*>([\s\S]*)<\/body>)'), resp.text)[0][0],
                                        'lxml')

            main_table = detial_soup.find('table', class_='MsoNormalTable')
            all_rows = main_table.find_all('tr')
            start_row = len(all_rows) - 9

            wenhao = all_rows[start_row + 0].find_all('td')[1].text
            geren = all_rows[start_row + 1].find_all('td')[2].text
            danwei = all_rows[start_row + 2].find_all('td')[2].text
            faren = all_rows[start_row + 3].find_all('td')[1].text
            content = all_rows[start_row + 4].find_all('td')[1].text
            yiju = all_rows[start_row + 5].find_all('td')[1].text
            jieguo = all_rows[start_row + 6].find_all('td')[1].text
            jiguan = all_rows[start_row + 7].find_all('td')[1].text
            riqi = all_rows[start_row + 8].find_all('td')[1].text
            CUR.execute(SQL, (
                title, url, source, wenhao, geren, danwei, faren, content, yiju, jieguo, jiguan, riqi, CRAWL_ID,
                datetime.datetime.now()))

            DB.commit()
            print(wenhao, url)
            print('---------------------------------------------')
        except:
            print(traceback.format_exc())
            print()
            insert_exception(title, url)


def yinjianhui(url):
    big_num = 10000
    for page_no in range(1, big_num):
        time.sleep(0.5)
        print('当前页 {0}'.format(str(page_no)))
        resp = requests.get(url.format(str(page_no)), headers=header)
        soup = BeautifulSoup(resp.content, 'lxml')
        parse_yinjianhui(soup)

        if soup.find('a', text='下页'):
            continue
        else:
            break


def insert_exception(title, url):
    try:
        sql = 'insert into bi.yingbaojian_exception values(%s, %s, %s)'
        CUR.execute(sql, (title, url, datetime.datetime.now()))
        DB.commit()
    except:
        print(traceback.format_exc())
        print('')


yinjianhui(FENJU_URL)

DB.close()
