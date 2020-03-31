import datetime
import math
import bs4
import pandas as pd
import random
import re
import time
import traceback
import random
import time
from traceback import format_exc

from bs4 import BeautifulSoup

COOKIE = 'UM_distinctid=168ff3f9aac216-04ac55c276ed71-675c772b-144000-168ff3f9aad82; zg_did=%7B%22did%22%3A%20%22168ff3f9adf2e2-0164f0b569bc1e-675c772b-144000-168ff3f9ae02d%22%7D; _uab_collina=155047058565614151101428; acw_tc=6f0a2f9915504705856976240e7a75945673940ac38301b788cc1fbfb4; QCCSESSID=afacsfdc10cjbo1kqvgfqrcoe0; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1551693348,1551713069,1552028861,1552618373; CNZZDATA1254842228=1663761244-1550466015-https%253A%252F%252Fwww.baidu.com%252F%7C1552619238; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1552620357; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201552625849646%2C%22updated%22%3A%201552625849646%2C%22info%22%3A%201552028860627%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.qichacha.com%22%2C%22cuid%22%3A%20%22aaddd500ad6a8a464c91bac9698fcad7%22%7D'

udf_header = {
    'Host': 'www.qichacha.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    # 'Referer': 'https://www.qichacha.com/search?key=%E6%B1%89%E6%9F%8F%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8',
    'Cookie': COOKIE,
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

SEARCH_URL = 'https://www.qichacha.com/search?key={0}'

import requests


# 1. 请求 search results 页面
# 2. 从search results 里获得对应实体的详细信息页面
# 3. 请求详细信息页面，并解析分支机构
# 4. 单独请求法律文书页面

def handle_search_results_page(entity_name):
    url = SEARCH_URL.format(entity_name)
    try:
        resp = requests.get(url, headers=udf_header, timeout=60)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'lxml')

            for t in soup.find_all('a', attrs={'class': 'ma_h1'}):
                if t.text == entity_name:
                    page_url = 'https://www.qichacha.com' + t.attrs['href']
                    firm_id = re.findall(re.compile('firm_(\S*).html'), page_url)[0]
                    return firm_id, page_url
        else:
            print('获取搜索结果页面失败 | {0}'.format(url))
            print('status code: {0}'.format(resp.status_code))
    except:
        print('网络连接错误 | {0}'.format(url))
        print(traceback.format_exc())


import pymysql

db = pymysql.connect("localhost", "root", "1234.abcd", "bi")

info = []


def store_detail_url():
    for name in ['天津房地产集团有限公司', '天津新金融投资有限责任公司', '天津市政投资有限公司', '天津蓟州新城建设投资有限公司', '中储发展股份有限公司', '海航凯撒旅游集团股份有限公司',
                 '冀中能源峰峰集团有限公司',
                 '河钢股份有限公司', '天津星城投资发展有限公司', '天津滨海新区建设投资集团有限公司', '天津保税区投资控股集团有限公司']:
        id, url = handle_search_results_page(name)
        info.append([id, name, url])
    cursor = db.cursor()
    sql = 'insert into webpage_info(firm_id, firm_name, url) values(%s, %s, %s)'
    cursor.executemany(sql, info)
    db.commit()


def parse_gudong():
    cur = db.cursor()
    cur.execute('select firm_id, firm_name, url from webpage_info')
    firms = cur.fetchall()
    for firm in firms:
        firm_id, firm_name, url = firm
        resp = requests.get(url, headers=udf_header, timeout=60)
        print(firm)
        soup = BeautifulSoup(resp.content, 'lxml')
        gudong_list = []
        # 股东信息  直接从本页解析，没有分析
        Sockinfo = soup.find('a', attrs={'data-pos': 'Sockinfo'})
        if Sockinfo:
            print('股东信息: ' + Sockinfo.find('span').text)
            sock_section = soup.find('section', id='Sockinfo')
            for gudong in sock_section.find_all('table', attrs={'class': 'insert-table'}):
                a = gudong.find('a')
                if a:
                    gudong_name = a.text.strip()
                    gudong_url = 'https://www.qichacha.com' + a.attrs['href'].strip()
                    gudong_id = re.findall(re.compile('firm_(\S*).html'), gudong_url)
                    if gudong_id:
                        gudong_id = gudong_id[0]
                    else:
                        gudong_id = ''

                else:
                    gudong_name = gudong.find('div', attrs={'class': 'whead-text'}).text.strip()
                    gudong_url = ''
                    gudong_id = ''
                gudong_list.append([firm_id, gudong_name, gudong_id, gudong_url, ])

            temp_row = 0
            for row in sock_section.find_all('tr')[1:]:
                tds = row.find_all('td', attrs={'class': 'text-center'})
                if len(tds) == 0:
                    continue
                elif len(tds) == 3:
                    chigubili, renjiaochuzi, renjiaoriqi = [
                        td.text.replace('\n', '').replace(' ', '').strip() for td in tds]
                    shijiaochuzi, shijiaoriqi = '', ''
                elif len(tds) == 5:
                    chigubili, renjiaochuzi, renjiaoriqi, shijiaochuzi, shijiaoriqi = [
                        td.text.replace('\n', '').replace(' ', '').strip() for td in tds]
                else:
                    print('{0} 列数不对'.format(firm_name))
                    continue
                if tds:
                    gudong_list[temp_row].extend(
                        [chigubili, renjiaochuzi, renjiaoriqi, shijiaochuzi, shijiaoriqi, datetime.datetime.now()])
                    temp_row += 1
        print(gudong_list)
        cur.executemany('insert into gudong_info values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', gudong_list)
        db.commit()


def parse_fenzhi():
    cur = db.cursor()
    cur.execute('select firm_id, firm_name, url from webpage_info')
    firms = cur.fetchall()
    for firm in firms:
        firm_id, firm_name, url = firm
        resp = requests.get(url, headers=udf_header, timeout=60)
        print(firm)
        soup = BeautifulSoup(resp.content, 'lxml')
        fenzhi_list = []
        # 分支机构  直接从本页解析，没有分页
        subcom = soup.find('a', attrs={'data-pos': 'Subcom'})
        if subcom:
            print('分支机构: ' + subcom.find('span').text)
            subcom_section = soup.find('section', id='Subcom')
            for fenzhi in subcom_section.find_all('div', attrs={'class': 'whead-text'}):
                name = fenzhi.find('a').text.strip()
                fenzhi_url = 'https://www.qichacha.com' + fenzhi.find('a').attrs['href'].strip() + '.html'
                fenzhi_id = re.findall(re.compile('firm_(\S*).html'), fenzhi_url)
                if fenzhi_id:
                    fenzhi_id = fenzhi_id[0]
                else:
                    fenzhi_id = ''
                fenzhi_list.append([firm_id, name, fenzhi_url, fenzhi_id, datetime.datetime.now()])
        else:
            print('分支机构: 0')

        print(fenzhi_list)
        cur.executemany('insert into fenzhijigou_info values(%s, %s, %s, %s, %s)', fenzhi_list)
        db.commit()


def parse_touzi():
    cur = db.cursor()
    cur.execute('select firm_id, firm_name, url from webpage_info')
    TOUZI_URL = 'https://www.qichacha.com/company_getinfos?unique={0}&companyname={1}&p={2}&tab=base&box=touzi'
    firms = cur.fetchall()
    for firm in firms:
        firm_id, firm_name, url = firm
        time.sleep(2)
        resp = requests.get(url, headers=udf_header, timeout=60)
        print(firm)
        soup = BeautifulSoup(resp.content, 'lxml')
        touzi_list = []
        # 对外投资  构建url循环获取
        touzi = soup.find('a', attrs={'data-pos': 'touzilist'})
        if touzi:
            print('分支机构: ' + touzi.find('span').text)
            touzi_count = int(touzi.find('span').text)

            page_count = math.ceil(touzi_count / 10)

            for page_no in range(1, page_count + 1):
                print('当前页数: ' + str(page_no))
                curr_url = TOUZI_URL.format(firm_id, firm_name, page_no)
                print(curr_url)
                time.sleep(2)
                resp = requests.get(curr_url, headers=udf_header, timeout=60)

                soup = BeautifulSoup(resp.content, 'lxml')

                for tag in [t for t in soup.find('tbody').children if isinstance(t, bs4.element.Tag)][1:]:
                    tds = [t for t in list(tag.children) if isinstance(t, bs4.element.Tag)]
                    touzi_firm_name = tds[0].find('a').text
                    touzi_firm_url = 'https://www.qichacha.com' + tds[0].find('a').attrs['href']
                    touzi_firm_id = re.findall(re.compile('firm_(\S*).html'), touzi_firm_url)[0]

                    represent = tds[1].find('a').text.replace('\n', '').replace(' ', '')
                    ziben = tds[2].text.replace('\n', '').replace(' ', '')
                    bili = tds[3].text.replace('\n', '').replace(' ', '')
                    chengliriqi = tds[4].text.replace('\n', '').replace(' ', '')
                    status = tds[5].text.replace('\n', '').replace(' ', '')

                    touzi_list.append(
                        [firm_id, touzi_firm_name, touzi_firm_id, touzi_firm_url, represent, ziben, bili,
                         chengliriqi, status, datetime.datetime.now()])

                    print(firm_id, touzi_firm_name, touzi_firm_id, touzi_firm_url, represent, ziben, bili,
                          chengliriqi, status)



        else:
            print('对外投资: 0')

        # print(touzi_list)
        cur.executemany('insert into touzi_info values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', touzi_list)
        db.commit()


def parse_wenshu():
    cur = db.cursor()
    cur.execute('select touzi_firm_id, touzi_firm_name, touzi_firm_url from bi.touzi_info')
    WENSHU_URL = 'https://www.qichacha.com/company_getinfos?unique={0}&companyname={1}&p={2}&tab=susong&box=wenshu'
    firms = cur.fetchall()
    for firm in firms:
        firm_id, firm_name, url = firm
        time.sleep(2)
        print(firm)
        resp = requests.get(url, headers=udf_header, timeout=60)
        soup = BeautifulSoup(resp.content, 'lxml')
        wenshu_list = []
        # 对外投资  构建url循环获取
        wenshu = soup.find('a', attrs={'data-pos': 'wenshulist'})
        if wenshu:
            print('裁判文书: ' + wenshu.find('span').text)
            try:
                wenshu_count = int(wenshu.find('span').text)
            except ValueError:
                curr_url = WENSHU_URL.format(firm_id, firm_name, 1)
                resp = requests.get(curr_url, headers=udf_header, timeout=60)
                soup = BeautifulSoup(resp.content, 'lxml')
                wenshu_count = int(soup.find('span', class_='tbadger').text)

            page_count = math.ceil(wenshu_count / 10)

            for page_no in range(1, page_count + 1):
                print('当前页数: ' + str(page_no))
                curr_url = WENSHU_URL.format(firm_id, firm_name, page_no)
                print(curr_url)
                resp = requests.get(curr_url, headers=udf_header, timeout=60)
                time.sleep(2)

                soup = BeautifulSoup(resp.content, 'lxml')

                for tag in soup.find('table').find_all('tr')[1:]:
                    tds = tag.find_all('td')[1:]
                    wenshu_name = tds[0].find('a').text
                    wenshu_url = 'https://www.qichacha.com' + tds[0].find('a').attrs['href']

                    reason = tds[1].text.replace('\n', '').replace(' ', '')
                    issue_date = tds[2].text.replace('\n', '').replace(' ', '')
                    wenshu_number = tds[3].text.replace('\n', '').replace(' ', '')
                    role = tds[4].text.replace('\n', '').replace(' ', '')
                    court = tds[5].text.replace('\n', '').replace(' ', '')

                    wenshu_list.append(
                        [firm_id, wenshu_name, wenshu_url, reason, issue_date, wenshu_number, role,
                         court, datetime.datetime.now()])

                    print(firm_id, wenshu_name, reason, issue_date, wenshu_number, role, court)
                    print('')
                    print('**********************************************************************')



        else:
            print('裁判文书: 0')

        # print(touzi_list)
        try:
            cur.executemany(
                'insert into wenshu_info(firm_id, wenshu_title, wenshu_url, reason, issue_date, wenshubianhao, role, court, crawl_date) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                wenshu_list)
            db.commit()
        except:
            print('{0} 爬取失败'.format(firm_name))
            print(traceback.format_exc())


# 解析行政处罚
def parse_penalty():
    cur = db.cursor()
    cur.execute('select touzi_firm_id, touzi_firm_name, touzi_firm_url from bi.touzi_info')
    FENGXIAN_URL = 'https://www.qichacha.com/company_getinfos?unique={0}&companyname={1}&tab=fengxian'
    firms = cur.fetchall()
    for firm in firms:
        firm_id, firm_name, url = firm
        time.sleep(2)
        resp = requests.get(url, headers=udf_header, timeout=60)
        print(firm)
        soup = BeautifulSoup(resp.content, 'lxml')
        chufa_list = []
        # 行政处罚  构建url循环获取
        wenshu = soup.find('a', attrs={'data-pos': 'penaltylist'})
        if wenshu:
            print('行政处罚: ' + wenshu.find('span').text)
            time.sleep(1)
            resp = requests.get(FENGXIAN_URL.format(firm_id, firm_name), headers=udf_header)
            print(FENGXIAN_URL.format(firm_id, firm_name))
            soup = BeautifulSoup(resp.content, 'lxml')
            # 行政处罚 工商局
            chufa_01 = soup.find('section', id='penaltylist').find('table')
            if chufa_01:
                for row in chufa_01.find_all('tr')[1:]:
                    tds = row.find_all('td')[1:]
                    number = tds[0].text.replace('\n', '').replace(' ', '')
                    content = tds[1].text.replace('\n', '').replace(' ', '') + ';' + tds[2].text.replace('\n',
                                                                                                         '').replace(
                        ' ', '')
                    date = tds[5].text.replace('\n', '').replace(' ', '')
                    organ = tds[4].text.replace('\n', '').replace(' ', '')
                    reason = ''
                    result = ''
                    source = '国家企业信用信息公示系统'

                    chufa_list.append(
                        [firm_id, number, content, date, organ, reason, result, source, datetime.datetime.now()])
                    print(firm_id, number, content, date, organ, reason, result, source)
                    print('')
                    print('**********************************************************************')

            # 行政处罚 信用中国
            chufa_02 = soup.find('span', text=re.compile('行政处罚 \[信用中国\]'))
            if chufa_02:
                for row in chufa_02.parent.parent.find('table').find_all('tr')[1:]:
                    tds = row.find_all('td')
                    id = tds[1].find('a').attrs['onclick']
                    id = re.findall(re.compile('xzcfView\("(\S*)"\)'), id)
                    time.sleep(1)
                    resp = requests.post('https://www.qichacha.com/company_xzcfView', data={'id': id},
                                         headers=udf_header).json()

                    number = resp['data']['document_no']
                    content = resp['data']['reason']
                    date = resp['data']['decide_date']
                    organ = resp['data']['office_no']
                    reason = ''
                    result = ''
                    source = '信用中国'

                    chufa_list.append(
                        [firm_id, number, content, date, organ, reason, result, source, datetime.datetime.now()])

                    print(firm_id, number, content, date, organ, reason, result, source)
                    print('')
                    print('**********************************************************************')



        else:
            print('行政处罚: 0')

        # print(touzi_list)
        try:
            cur.executemany(
                'insert into penalty_info values(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                chufa_list)
            db.commit()
        except:
            print('{0} 爬取失败'.format(firm_name))
            print(traceback.format_exc())


def parse_huanbaochufa():
    cur = db.cursor()
    cur.execute('select touzi_firm_id, touzi_firm_name, touzi_firm_url from bi.touzi_info')
    FENGXIAN_URL = 'https://www.qichacha.com/company_getinfos?unique={0}&companyname={1}&tab=fengxian'
    firms = cur.fetchall()
    for firm in firms:
        firm_id, firm_name, url = firm
        print(firm)
        chufa_list = []
        # 行政处罚  构建url循环获取
        time.sleep(1)
        resp = requests.get(FENGXIAN_URL.format(firm_id, firm_name), headers=udf_header)
        # print(FENGXIAN_URL.format(firm_id, firm_name))
        soup = BeautifulSoup(resp.content, 'lxml')
        # 环保处罚
        chufa = soup.find('section', id='envlist')
        if chufa and chufa.find('table'):
            print('环保处罚: {0}'.format(str(len(chufa.find('table').find_all('tr')) - 1)))
            for row in chufa.find('table').find_all('tr')[1:]:
                tds = row.find_all('td')
                id = tds[1].find('a').attrs['onclick']
                id = re.findall(re.compile('envDetail\("(\S*)"\)'), id)[0]
                time.sleep(1)
                resp = requests.get('https://www.qichacha.com/company_envDetail?id=' + id, headers=udf_header).json()

                number = resp['data']['CaseNo']
                illtype = resp['data']['IllegalType']
                content = resp['data']['PunishReason']
                result = resp['data']['PunishmentResult']
                organ = resp['data']['PunishGov']
                decide_date = time.strftime('%Y-%m-%d', time.localtime(resp['data']['PunishDate']))
                according = resp['data']['PunishBasis']

                chufa_list.append(
                    [firm_id, number, illtype, content, result, organ, decide_date, according, datetime.datetime.now()])

                print(firm_id, number, illtype, content, result, organ, decide_date, according, )
                print('')
                print('**********************************************************************')
        else:
            print('环保处罚: 0')
        # print(touzi_list)
        try:
            cur.executemany(
                'insert into env_penalty_info values(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                chufa_list)
            db.commit()
        except:
            print('{0} 爬取失败'.format(firm_name))
            print(traceback.format_exc())


def parse_bond():
    cur = db.cursor()
    cur.execute('select firm_id, firm_name, url from webpage_info')
    BOND_URL = 'https://www.qichacha.com/company_getinfos?unique={0}&companyname={1}&p={2}&tab=run&box=creditor'
    firms = cur.fetchall()
    for firm in firms:
        firm_id, firm_name, url = firm
        time.sleep(2)
        resp = requests.get(url, headers=udf_header, timeout=60)
        print(firm)
        soup = BeautifulSoup(resp.content, 'lxml')
        bond_list = []
        # 债券信息  构建url循环获取
        bond = soup.find('a', attrs={'data-pos': 'creditorlist'})
        if bond:
            print('债券信息: ' + bond.find('span').text)
            bond_count = int(bond.find('span').text)

            page_count = math.ceil(bond_count / 10)

            for page_no in range(1, page_count + 1):
                print('当前页数: ' + str(page_no))
                curr_url = BOND_URL.format(firm_id, firm_name, page_no)
                print(curr_url)
                time.sleep(2)
                resp = requests.get(curr_url, headers=udf_header, timeout=60)

                soup = BeautifulSoup(resp.content, 'lxml')

                for tag in soup.find('table').find_all('tr')[1:]:
                    tds = tag.find_all('td')
                    onclick = tds[1].find('a').attrs['onclick']
                    id = re.findall(re.compile('creditorDetail\("(\S*)",'), onclick)[0]
                    bond_detail_url = 'https://www.qichacha.com/company_creditorDetail?id=' + id

                    time.sleep(1)

                    resp = requests.get(bond_detail_url, headers=udf_header, timeout=60).json()

                    bond_name = resp['data']['FullName']
                    short_name = resp['data']['ShortName']
                    bond_code = resp['data']['BondCode']
                    bond_type = resp['data']['BondType']
                    mianzhi = resp['data']['BoundValue']
                    nianxian = resp['data']['YearLimit']
                    lilv = resp['data']['InterestRate']
                    daoqi = time.strftime('%Y-%m-%d', time.localtime(resp['data']['MaturityDate']))
                    duihuan = time.strftime('%Y-%m-%d', time.localtime(resp['data']['HonourDate']))
                    zhaipai = time.strftime('%Y-%m-%d', time.localtime(resp['data']['DelistDate']))
                    comment = resp['data']['InterestRateIntroduce']
                    jixifangshi = resp['data']['PlanBreathWay']
                    fuxifangshi = resp['data']['ServicingWay']
                    qixi = time.strftime('%Y-%m-%d', time.localtime(resp['data']['PayoutDate']))  # 起息
                    zhixi = time.strftime('%Y-%m-%d', time.localtime(resp['data']['CeaseDate']))  # 止息
                    fuxicishu = resp['data']['IsValid']
                    fuxiriqi = resp['data']['InterestPaymentDate']
                    price = resp['data']['OfferingPrice']
                    guimo = resp['data']['Issuance']
                    faxingriqi = time.strftime('%Y-%m-%d', time.localtime(resp['data']['ReleaseDate']))
                    shangshiriqi = time.strftime('%Y-%m-%d', time.localtime(resp['data']['LaunchDate']))
                    place = resp['data']['PublicPlaces']
                    dengji = resp['data']['CreditRating']

                    bond_list.append(
                        [firm_id, bond_name, short_name, bond_code, bond_type, mianzhi, nianxian,
                         lilv, daoqi, duihuan, zhaipai, comment, jixifangshi, fuxifangshi, qixi, zhixi, fuxicishu,
                         fuxiriqi, price,
                         guimo, faxingriqi, shangshiriqi, place, dengji, datetime.datetime.now()])

                    print(firm_id, bond_name, short_name, bond_code, bond_type)
                    print('')
                    print('**********************************************************************')



        else:
            print('裁判文书: 0')

        # print(touzi_list)
        cur.executemany(
            'insert into bond_info values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            bond_list)
        db.commit()


def parse_wenshu_detail():
    cur = db.cursor()
    cur.execute('SELECT id, wenshu_url FROM bi.wenshu_info where content is null')
    records = cur.fetchall()
    for r in records:
        time.sleep(0.8)
        id, url = r
        resp = requests.get(url, headers=udf_header, timeout=60)
        soup = BeautifulSoup(resp.content, 'lxml')
        try:
            a = soup.find('div', class_='des').find('a')
        except:
            print(traceback.format_exc())
            print(url)
            continue

        if a:
            source = a.text
            source_url = a.attrs['href']
        else:
            source = soup.find('div', class_='des').find('span', class_='from').text.replace('\n', '').replace(' ', '')
            source_url = ''

        content = soup.find('div', class_='qcc_law_doc')
        if content:
            content = content.text
        else:
            content = soup.find('div', id='wsview').text

        print(source_url, source)
        print('------------------------------------------------------')
        print()
        update_sql = 'update bi.wenshu_info set source = "{0}", source_url = "{1}", content = "{2}" where id = "{3}"'.format(
            source,
            source_url,
            content, id)
        try:
            cur.execute(update_sql)
            db.commit()
        except:
            print(traceback.format_exc())
            print('更新失败, 对应id: ' + str(id))


# parse_wenshu_detail()

def parse_tax_weifa():
    # 税收违法

    cur = db.cursor()
    cur.execute(
        '''
       select gudong_id, gudong, gudong_url from bi.gudong_info where gudong_url != ''
        union
        select sub_firm_id, name, firm_url from bi.fenzhijigou_info
        union 
        select firm_id, firm_name, url from bi.webpage_info
        '''
    )
    TAX_URL = 'https://www.qichacha.com/company_getinfos?unique={0}&companyname={1}&p={2}&tab=run&box=creditor'
    firms = cur.fetchall()
    for firm in firms:
        firm_id, firm_name, url = firm
        time.sleep(2)
        resp = requests.get(url, headers=udf_header, timeout=60)
        print(firm)
        soup = BeautifulSoup(resp.content, 'lxml')
        bond_list = []
        # 债券信息  构建url循环获取
        tax = soup.find('a', attrs={'data-pos': 'taxillegallist'})
        if tax:
            print('税收违法: ' + tax.find('span').text)


def parse_beizhixingren():
    # 被执行人

    cur = db.cursor()
    cur.execute(
        '''
         select touzi_firm_id, touzi_firm_name, touzi_firm_url from bi.touzi_info
        '''
    )
    TAX_URL = 'https://www.qichacha.com/company_getinfos?unique={0}&companyname={1}&p={2}&tab=run&box=creditor'
    firms = cur.fetchall()
    for firm in firms:
        firm_id, firm_name, url = firm
        time.sleep(2)
        resp = requests.get(url, headers=udf_header, timeout=60)

        soup = BeautifulSoup(resp.content, 'lxml')
        zhixingren_list = []
        tax = soup.find('a', attrs={'data-pos': 'zhixinglist'})
        if tax:
            print(firm)
            print('被执行人: ' + tax.find('span').text)

            # sock_section = soup.find('section', id='zhixinglist')
            # for zhixingren in sock_section.find('table').find_all('tr')[2:]:
            #     content = zhixingren.find_all('td')[1].text
            #     punish_date = zhixingren.find_all('td')[2].text
            #     amount = zhixingren.find_all('td')[4].text
            #     zhixingren_list.append(
            #         [firm_id, content, punish_date, amount, datetime.datetime.now()])

        # print(zhixingren_list)
            cur.execute('insert into zhixingren(firm_id, url) values(%s,%s)', (firm_id, url))
            db.commit()


parse_beizhixingren()
db.close()
