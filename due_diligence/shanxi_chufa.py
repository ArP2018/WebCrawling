import datetime
import json
import math
import re
import time
import traceback

import bs4
import pymysql
import requests
from bs4 import BeautifulSoup

FIRST_URL = 'http://sthjt.shanxi.gov.cn/html/xzcfjd/index.html'
URL = 'http://sthjt.shanxi.gov.cn/html/xzcfjd/index_{0}.html'
DB = pymysql.connect("localhost", "root", "1234.abcd", "bi")
CUR = DB.cursor()
SQL = 'insert into huanbaochufa(title, url, wenhao, content, source, issue_date, crawl_id, crawl_date) values(%s, %s, %s,%s, %s, %s,%s,%s)'
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
}

CRAWL_ID = 111


def insert_exception(title, url):
    try:
        sql = 'insert into bi.yingbaojian_exception values(%s, %s, %s)'
        CUR.execute(sql, (title, url, datetime.datetime.now()))
        DB.commit()
    except:
        print(traceback.format_exc())
        print('')


def parse_chufa(soup: BeautifulSoup):
    for td in soup.find('ul', class_='list-details').find_all('li'):
        a = td.find('a')
        title = a.attrs['title']
        url = 'http://sthjt.shanxi.gov.cn' + a.attrs['href']
        source = '山西省环保厅'
        try:
            time.sleep(0.5)
            resp = requests.get(url, headers=header)
            detial_soup = BeautifulSoup(resp.content, 'lxml')

            content = detial_soup.find('div', class_='td-con').text

            CUR.execute(SQL, (
                title, url, title, content, source, '', CRAWL_ID, datetime.datetime.now()))

            DB.commit()
            print(title, url)
            print('---------------------------------------------')
        except:
            print(traceback.format_exc())
            print()
            insert_exception(title, url)


def shanxi():
    resp = requests.get(FIRST_URL, headers=header)
    soup = BeautifulSoup(resp.content, 'lxml')
    parse_chufa(soup)
    page_info = soup.find('div', class_='page-total').text
    tot = int(re.findall(re.compile('共 (\d*) 页'), page_info)[0])
    for page_no in range(2, tot + 1):
        time.sleep(0.5)
        print('当前页 {0}'.format(str(page_no)))
        resp = requests.get(URL.format(str(page_no)), headers=header)
        soup = BeautifulSoup(resp.content, 'lxml')
        parse_chufa(soup)


HENAN_URL = 'http://www.hnep.gov.cn/xxgk/hbywxxgk/jczf/xzcf/H6001040601index_{0}.htm'


def parse_henan_chufa(soup: BeautifulSoup):
    for li in soup.find('ul', class_='newslist').find_all('li'):
        wenhao = li.find('span', class_='list_hbwj1').text
        title = li.find('a').attrs['title']
        url = 'http://www.hnep.gov.cn' + li.find('a').attrs['href']

        source = '河南省环保厅'
        try:
            time.sleep(0.5)
            resp = requests.get(url, headers=header)
            detial_soup = BeautifulSoup(resp.content, 'lxml')

            content = detial_soup.find('div', id='BodyLabel').text

            CUR.execute(SQL, (
                title, url, wenhao, content, source, '', CRAWL_ID, datetime.datetime.now()))

            DB.commit()
            print(title, url)
            print('---------------------------------------------')
        except:
            print(traceback.format_exc())
            print()
            insert_exception(title, url)


def henan():
    # resp = requests.get(HENAN_URL.format('1'), headers=header)
    # soup = BeautifulSoup(resp.content, 'lxml')
    # parse_henan_chufa(soup)
    # page_info = soup.find('ul', class_='newslist').text
    # tot = int(re.findall(re.compile('当前第 \d* /(\d*) 页'), page_info)[0])
    for page_no in range(2, 12):
        time.sleep(0.5)
        print('当前页 {0}'.format(str(page_no)))
        resp = requests.get(HENAN_URL.format(str(page_no)), headers=header)
        soup = BeautifulSoup(resp.content, 'lxml')
        parse_henan_chufa(soup)


def parse_anhui_chufa(soup: BeautifulSoup):
    for li in soup.find('ul', class_='search_rc').find_all('dl'):
        title = wenhao = li.find('a').text
        url = 'http://sthjt.ah.gov.cn' + li.find('a').attrs['href']

        source = '安徽省环保厅'
        try:
            time.sleep(0.5)
            resp = requests.get(url, headers=header)
            detial_soup = BeautifulSoup(resp.content, 'lxml')

            content = detial_soup.find('div', class_='LitContentXXGK').text

            CUR.execute(SQL, (
                title, url, wenhao, content, source, '', CRAWL_ID, datetime.datetime.now()))

            DB.commit()
            print(title, url)
            print('---------------------------------------------')
        except:
            print(traceback.format_exc())
            print()
            insert_exception(title, url)


ANHUI_URL_01 = 'http://sthjt.ah.gov.cn/pages/SearchList.aspx?Stype=0&DateType=3000&SearchKey=%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A&MenuID=190000&page={0}'
ANHUI_URL_02 = 'http://sthjt.ah.gov.cn/pages/SearchList.aspx?Stype=0&DateType=3000&SearchKey=%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A&MenuID=010301&page={0}'


def anhui():
    for url in (ANHUI_URL_01, ANHUI_URL_02):
        for page_no in range(1, 10000):
            time.sleep(0.5)
            print('当前页 {0}'.format(str(page_no)))
            resp = requests.get(url.format(str(page_no)), headers=header)
            soup = BeautifulSoup(resp.content, 'lxml')
            parse_anhui_chufa(soup)

            if soup.find('a', text='尾页'):
                continue
            else:
                break


def parse_shandong_chufa(soup: BeautifulSoup):
    table_tag = \
        [t for t in soup.find('td', text='环境行政处罚').parent.parent.parent.parent.parent.parent.parent.parent.children if
         isinstance(t, bs4.element.Tag)][3].find('table')
    for tr in table_tag.find_all('tr'):
        if tr.find('a'):
            title = wenhao = tr.find('a').attrs['title']
            url = 'http://xxgk.sdein.gov.cn/xxgkml/hbzfjc' + tr.find('a').attrs['href'].lstrip('.')

            source = '山东省环保厅'
            try:
                time.sleep(0.5)
                resp = requests.get(url, headers=header)
                detial_soup = BeautifulSoup(resp.content, 'lxml')

                content = detial_soup.find('td', class_='zw').text

                CUR.execute(SQL, (
                    title, url, wenhao, content, source, '', CRAWL_ID, datetime.datetime.now()))

                DB.commit()
                print(title, url)
                print('---------------------------------------------')
            except:
                print(traceback.format_exc())
                print()
                insert_exception(title, url)


SD_FIRST_URL = 'http://xxgk.sdein.gov.cn/xxgkml/hbzfjc/index.html'
SD_URL = 'http://xxgk.sdein.gov.cn/xxgkml/hbzfjc/index_{0}.html'


def shandong():
    print('当前页 1')
    resp = requests.get(SD_FIRST_URL, headers=header)
    soup = BeautifulSoup(resp.content, 'lxml')
    parse_shandong_chufa(soup)

    tot = int(re.findall(re.compile('共有 (\d*) 页'), resp.content)[0])

    for page_no in range(1, 4):
        time.sleep(0.5)
        print('当前页 {0}'.format(str(page_no + 1)))
        resp = requests.get(SD_URL.format(str(page_no)), headers=header)
        soup = BeautifulSoup(resp.content, 'lxml')
        parse_shandong_chufa(soup)


def parse_tianjin_chufa(url, soup: BeautifulSoup):
    [s.extract() for s in soup('style')]
    [s.extract() for s in soup('script')]
    lis = soup.find('ul', class_='ullist').find_all('li')

    for li in lis:
        if li.find('a'):
            title = wenhao = li.find('a').text
            detail_url = url + li.find('a').attrs['href'].lstrip('.')

            source = '天津市环保局'
            try:
                time.sleep(0.5)
                resp = requests.get(detail_url, headers=header)
                detial_soup = BeautifulSoup(resp.content, 'lxml')
                [s.extract() for s in detial_soup('style')]
                [s.extract() for s in detial_soup('script')]

                content = detial_soup.find('table', id='printContent').text.strip()

                CUR.execute(SQL, (
                    title, detail_url, wenhao, content, source, '', CRAWL_ID, datetime.datetime.now()))

                DB.commit()
                print(title, detail_url)
                print('---------------------------------------------')
            except:
                print(traceback.format_exc())
                print()
                insert_exception(title, detail_url)


TIANJIN_URL_01 = 'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/decided_punishment'
TIANJIN_URL_02 = 'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/environmentalviolations_timelimit_decision'


def tianjin():
    page_no = 1
    for url in (TIANJIN_URL_01, TIANJIN_URL_02):
        time.sleep(0.5)
        print('当前页 {0}'.format(str(page_no)))
        resp = requests.get(url, headers=header)
        soup = BeautifulSoup(resp.content, 'lxml')
        parse_tianjin_chufa(url, soup)

        page_info = soup.find('a', id='pagenav_tail').attrs['href']
        tot = int(re.findall(re.compile('index_(\d*).html'), page_info)[0])
        for page_no in range(1, tot + 1):
            print('当前页 {0}'.format(str(page_no + 1)))
            next_page = url + '/index_{0}.html'.format(page_no)
            resp = requests.get(next_page, headers=header)
            soup = BeautifulSoup(resp.content, 'lxml')
            parse_tianjin_chufa(url, soup)


def parse_hebei_chufa(resp):
    for item in resp['list']:
        try:
            title = wenhao = item['document_number']
            source = '河北省环保厅'
            url = 'http://xzzf.hbzwfw.gov.cn/punish/getPunishById?id=' + str(item['id'])
            content = item['relative_name'] + '\n' + item['illegal_fact'] + '\n' + item['cause'] + '\n' + item[
                'punish_content'] + '\n' + item['punish_result'] + '\n' + item['punish_organname'] + '\n' + item[
                          'punish_date']
            CUR.execute(SQL, (
                title, url, wenhao, content, source, item['punish_date'], CRAWL_ID, datetime.datetime.now()))

            DB.commit()
            print(title, url)
            print('---------------------------------------------')
        except:
            print(traceback.format_exc())
            print()
            insert_exception(title, url)


HEBEI_URL = 'http://xzzf.hbzwfw.gov.cn/punish/getpunish'


def hebei():
    curpage = 1
    data = {
        'curpage': curpage,
        'departId': 2122,
        'cityId': '',
        'gkType': 120,
        'selType': 320
    }

    resp = requests.post(HEBEI_URL, data=data, headers=header).json()
    parse_hebei_chufa(resp)
    tot = math.ceil(resp['page']['total'] / 10)

    for page_no in range(2, tot + 1):
        data = {
            'curpage': page_no,
            'departId': 2122,
            'cityId': '',
            'gkType': 120,
            'selType': 320
        }

        resp = requests.post(HEBEI_URL, data=data, headers=header).json()
        parse_hebei_chufa(resp)


def parse_nmg_chufa(soup: BeautifulSoup):
    trs = soup.find('table').find_all('tr')
    for tr in trs[1:]:
        tds = tr.find_all('td')
        try:
            title = tds[2].text.strip()
            wenhao = ''
            source = '内蒙古环保厅'
            url = 'http://sthjt.nmg.gov.cn/xxgk/base/data-selection!secondPage.action?menuCode=xzcf&secondType=JCZFZJZCDCFJD'
            content = '\n'.join([td.text.strip() for td in tds])
            punish_date = tds[-1].text.strip()
            CUR.execute(SQL, (
                title, url, wenhao, content, source, punish_date, CRAWL_ID, datetime.datetime.now()))

            DB.commit()
            print(title, url)
            print('---------------------------------------------')
        except:
            print(traceback.format_exc())
            print()
            insert_exception(title, url)


NMG_URL = 'http://sthjt.nmg.gov.cn/xxgk/base/data-selection!list.action'


# 内蒙古
def nmg():
    curpage = 1
    data_01 = {
        'page.pageNo': curpage,
        'typeCode': 'JCZFZJZCDCFJD',
        'tablename': 'JGXXGK.T_JCZF_ZJZCDCFJD',
        'queryUrl': '040',
        'page.pageSize': 10
    }

    data_02 = {
        'page.pageNo': curpage,
        'typeCode': 'JCZFWFXWXQZG',
        'tablename': 'JJGXXGK.T_JCZF_WFXWXQZG',
        'queryUrl': '040',
        'page.pageSize': 10
    }
    for data in (data_01, data_02):
        resp = requests.post(NMG_URL, data=data, headers=header)
        soup = BeautifulSoup(resp.text, 'lxml')
        parse_nmg_chufa(soup)
        tot = int(soup.find('span', id='pagelimit').text)

        for page_no in range(2, tot + 1):
            data['page.pageNo'] = page_no
            print('当前页 ' + str(page_no))
            resp = requests.post(NMG_URL, data=data, headers=header)
            soup = BeautifulSoup(resp.text, 'lxml')
            parse_nmg_chufa(soup)

tianjin()