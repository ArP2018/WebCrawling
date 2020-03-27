import json
import random
import re
import time
import traceback
from copy import copy

import requests
from bs4 import BeautifulSoup

from manager import ProxyManager
from settings import CRAWLED_SITES, USER_AGENTS, PHANTOMJS_PATH, CHROME_DRIVER_PATH
from utils import Util


class Crawler:
    def __init__(self):
        self.header = {'user-agent': random.choice(USER_AGENTS)}

    # 西祠代理
    def _crawl_site_0(self):
        '''
        爬取西刺代理前四页的IP
        :return:
        '''
        for i in range(1, 5):
            url = 'https://www.xicidaili.com/nn/{0}'.format(i)

            resp = requests.get(url, headers=self.header)
            soup = BeautifulSoup(resp.text, 'lxml')

            rows = soup.find('table', id='ip_list').find_all('tr')
            for row in rows[1:]:
                tds = row.find_all('td')
                item = {
                    'ip': tds[1].text,
                    'port': tds[2].text,
                    'type': tds[5].text
                }
                ProxyManager.feed_pool(json.dumps(item))

    # 快代理
    def _crawl_site_1(self):
        '''
        爬取快代理前三页的ip
        :return:
        '''
        for i in range(1, 4):
            url = 'https://www.kuaidaili.com/free/inha/{0}'.format(i)

            resp = requests.get(url, headers=self.header)
            soup = BeautifulSoup(resp.text, 'lxml')

            rows = soup.find('div', id='list').find_all('tr')
            for row in rows[1:]:
                tds = row.find_all('td')
                item = {
                    'ip': tds[0].text,
                    'port': tds[1].text,
                    'type': tds[3].text
                }
                ProxyManager.feed_pool(json.dumps(item))

            time.sleep(2)

    # 极速代理
    def _crawl_site_2(self):
        '''
        爬取极速代理前10页
        :return:
        '''
        for i in range(1, 11):
            url = 'http://www.superfastip.com/welcome/freeip/{0}'.format(i)

            resp = requests.get(url, headers=self.header)
            soup = BeautifulSoup(resp.text, 'lxml')

            rows = soup.find_all('div', class_='row clearfix')[2].find_all('tr')
            for row in rows[1:]:
                tds = row.find_all('td')
                item = {
                    'ip': tds[0].text,
                    'port': tds[1].text,
                    'type': tds[3].text
                }
                ProxyManager.feed_pool(json.dumps(item))

    def _crawl_site_3(self):
        '''
        爬取无忧免费代理,只有10个
        :return:
        '''
        url = 'http://www.data5u.com/'
        resp = requests.get(url, headers=self.header)
        soup = BeautifulSoup(resp.text, 'lxml')

        rows = soup.find_all('ul', class_='l2')
        for row in rows:
            tds = row.find_all('li')
            item = {
                'ip': tds[0].text,
                'port': tds[1].text,
                'type': tds[3].text
            }
            ProxyManager.feed_pool(json.dumps(item))

    def _crawl_site_4(self):
        '''
        云代理,爬取10页
        :return:
        '''
        for i in range(1, 11):
            url = 'http://www.ip3366.net/?stype=1&page={0}'.format(i)
            resp = requests.get(url, headers=self.header)
            soup = BeautifulSoup(resp.text, 'lxml')

            rows = soup.find('div', id='list').find_all('tr')
            for row in rows[1:]:
                tds = row.find_all('td')
                item = {
                    'ip': tds[0].text,
                    'port': tds[1].text,
                    'type': tds[3].text
                }
                ProxyManager.feed_pool(json.dumps(item))

    def _crawl_site_5(self):
        '''
        小舒代理,爬取最近两天更新的代理
        :return:
        '''
        main_url = 'http://www.xsdaili.com'
        resp = requests.get(main_url, headers=self.header)
        soup = BeautifulSoup(resp.text, 'lxml')

        urls = [u.find('a').attrs['href'] for u in soup.find_all('div', class_='title')]

        for url in urls[0:2]:
            resp = requests.get(main_url + url, headers=self.header)
            soup = BeautifulSoup(resp.content, 'lxml')

            text = soup.find('div', class_='cont').text
            pattern = '((\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])):(\d*)@(HTTP|HTTPS)'

            ip_list = re.findall(pattern, text)
            for ip_items in ip_list:
                item = {
                    'ip': ip_items[0],
                    'port': ip_items[5],
                    'type': ip_items[-1]
                }
                ProxyManager.feed_pool(json.dumps(item))

    def _crawl_site_6(self):
        '''
        站大爷代理,爬取最近三次更新的代理
        :return:
        '''
        main_url = 'http://ip.zdaye.com/dayProxy.html'

        resp = requests.get(main_url, self.header)
        soup = BeautifulSoup(resp.content, 'lxml')

        urls = [u.find('a').attrs['href'] for u in soup.find_all('h3', class_='thread_title')]

        header = copy(self.header)
        header['referer'] = main_url
        for url in urls[0:3]:
            resp = requests.get('http://ip.zdaye.com' + url, headers=header)
            soup = BeautifulSoup(resp.content, 'lxml')
            text = soup.find('div', class_='cont').text
            pattern = '((\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])):(\d*)@(HTTP|HTTPS)'

            ip_list = re.findall(pattern, text)
            for ip_items in ip_list:
                item = {
                    'ip': ip_items[0],
                    'port': ip_items[5],
                    'type': ip_items[-1]
                }
                # print(item)
                ProxyManager.feed_pool(json.dumps(item))

    def _crawl_site_7(self):
        '''
        米扑代理，游客只有第一页可见
        :return:
        '''
        url = 'https://proxy.mimvp.com/freeopen.php'
        resp = requests.get(url, headers=self.header)
        soup = BeautifulSoup(resp.text, 'lxml')

        rows = soup.find('div', class_='free-list').find_all('tr')
        for row in rows[1:]:
            tds = row.find_all('td')
            item = {
                'ip': tds[0].text,
                'port': tds[1].text,  # 需要ocr将图片内容转成文本
                'type': tds[3].text
            }
            ProxyManager.feed_pool(json.dumps(item))

    def _crawl_site_8(self):
        '''
        西拉代理
        :return:
        '''
        url = 'http://www.xiladaili.com'
        resp = requests.get(url, headers=self.header, )
        soup = BeautifulSoup(resp.text, 'lxml')

        tables = soup.find_all('table', class_='fl-table')
        # 爬取HTTP和HTTPS两块
        for t in tables[1:3]:
            for row in t.find_all('tr')[2:]:
                tds = row.find_all('td')
                ip, port = tds[0].text.split(':')
                item = {
                    'ip': ip,
                    'port': port,
                    'type': tds[2].text
                }
                print(item)
                ProxyManager.feed_pool(json.dumps(item))

    def _crawl_site_9(self):
        '''
        泥马代理
        :return:
        '''
        url = 'http://www.nimadaili.com'
        resp = requests.get(url, headers=self.header)
        soup = BeautifulSoup(resp.text, 'lxml')

        tables = soup.find_all('div', id='overflow')
        # 爬取HTTP和HTTPS两块
        for t in tables[2:]:
            for row in t.find_all('tr')[1:-1]:
                tds = row.find_all('td')
                ip, port = tds[0].text.split(':')
                item = {
                    'ip': ip,
                    'port': port,
                    'type': tds[2].text
                }
                # print(item)
                ProxyManager.feed_pool(json.dumps(item))

    def _crawl_site_10(self):
        '''
        万能代理前十页
        :return:
        '''
        for i in range(1, 11):
            url = 'http://wndaili.cn/?page={0}'.format(i)
            resp = requests.get(url, headers=self.header)
            soup = BeautifulSoup(resp.text, 'lxml')

            rows = soup.find('div', id='list').find_all('tr')
            for row in rows[1:]:
                tds = row.find_all('td')
                item = {
                    'ip': tds[0].text,
                    'port': tds[1].text,
                    'type': tds[3].text
                }
                # print(item)
                ProxyManager.feed_pool(json.dumps(item))

    def start_crawl(self):
        sites = CRAWLED_SITES.keys()
        for k in sites:
            func_name = '_crawl_site_%s' % k
            try:
                if getattr(self, func_name):
                    func = getattr(self, func_name)
                    func()
            except AttributeError:
                Util.log_to_file(traceback.format_exc(), 1)
                pass
            except:
                Util.log_to_file('Exception occured when crawl website {0}.'.format(CRAWLED_SITES[k]), 0)
                Util.log_to_file(traceback.format_exc(), 1)


if __name__ == '__main__':
    c = Crawler()
    c.start_crawl()
