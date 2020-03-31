import datetime
import re
import time
import traceback

import pymysql
from bs4 import BeautifulSoup

__author__ = 'Evan Yin'

# 原保监会处罚
# http://bxjg.circ.gov.cn/web/site0/tab5240/module14430/page1.htm

import requests

BASE_URL = 'http://bxjg.circ.gov.cn/web/site0/tab5240/module14430/page{0}.htm'
BAOJIANJU_URL = 'http://bxjg.circ.gov.cn/web/site0/tab5241/module14458/page{0}.htm'
DB = pymysql.connect("localhost", "root", "1234.abcd", "bi")
CUR = DB.cursor()
SQL = 'insert into chufa_info values(%s, %s, %s,%s, %s, %s,%s)'
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
}


def parse_baojianhui(soup: BeautifulSoup):
    tds = soup.find_all('td', class_='hui14')
    for td in tds:
        a = td.find('a')
        title = a.text
        url = 'http://bxjg.circ.gov.cn' + a.attrs['href']

        try:
            if '保监罚' in title:
                time.sleep(1.3)
                resp = requests.get(url, headers=header)
                soup = BeautifulSoup(resp.content, 'lxml')

                wenhao = soup.find('span', class_='xilanwb').find('p').text.replace('\n', '').strip()
                content = soup.find('span', class_='xilanwb').text
                issue_date = \
                    re.findall(re.compile('发布时间：([1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]))'), soup.text)[
                        0][0]
                CUR.execute(SQL, (title, wenhao, issue_date, content, '银保监官网', url, datetime.datetime.now()))

                DB.commit()
                print(wenhao, title, url)
                print('---------------------------------------------')
        except:
            print(traceback.format_exc())
            print()


def baojianhui():
    resp = requests.get(BASE_URL.format('1'), headers=header)
    soup = BeautifulSoup(resp.content, 'lxml')
    parse_baojianhui(soup)
    page_info = soup.find('td', class_='Normal').text
    page_count = int(re.findall(re.compile('当前页:1/(\d*)'), page_info)[0])

    for page_no in range(2, page_count + 1):
        time.sleep(1.2)
        print('当前页 {0}'.format(str(page_no)))
        resp = requests.get(BASE_URL.format(str(page_no)), headers=header)
        soup = BeautifulSoup(resp.content, 'lxml')
        parse_baojianhui(soup)


def insert_exception(title, url):
    try:
        sql = 'insert into bi.yingbaojian_exception values(%s, %s, %s)'
        CUR.execute(sql, (title, url, datetime.datetime.now()))
        DB.commit()
    except:
        print(traceback.format_exc())
        print('')


def parse_baojianju(soup):
    tds = soup.find_all('td', class_='hui14')
    for td in tds:
        a = td.find('a')
        title = a.attrs['title']
        url = 'http://bxjg.circ.gov.cn' + a.attrs['href']

        try:
            time.sleep(0.5)
            resp = requests.get(url, headers=header)
            soup = BeautifulSoup(resp.content, 'lxml')

            content = soup.find('span', class_='xilanwb').text
            issue_date = \
                re.findall(re.compile('发布时间：([1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]))'), soup.text)[0][0]
            CUR.execute(SQL, (title, title, issue_date, content, '银保监官网', url, datetime.datetime.now()))

            DB.commit()
            print(title, url)
            print('---------------------------------------------')
        except:
            print(traceback.format_exc())
            print()
            insert_exception(title, url)


def baojianju():
    baojianju_count = 856
    for page_no in range(580, 857):
        if page_no > baojianju_count:
            break
        time.sleep(0.5)
        print('当前页 {0}'.format(str(page_no)))
        resp = requests.get(BAOJIANJU_URL.format(str(page_no)), headers=header)
        soup = BeautifulSoup(resp.content, 'lxml')

        if page_no == 1:
            page_info = soup.find('td', class_='Normal').text
            baojianju_count = int(re.findall(re.compile('当前页:1/(\d*)'), page_info)[0])

        parse_baojianju(soup)


baojianju()

