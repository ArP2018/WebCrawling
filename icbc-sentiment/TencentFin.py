# encoding: utf-8
# 腾讯财经爬虫
# author: Yin Yalin
import re
import threading

from bs4 import BeautifulSoup

from logger import CustomLogging, LogType
from sougou import Sougou


class TencentFin(Sougou):
    def __init__(self, site):
        super().__init__(site)
        self.name = '腾讯财经'

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': re.compile('(Cnt-Main-Article-QQ)|(ArticleCnt)')}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            pass


if __name__ == '__main__':
    test = TencentFin()
    test.start_crawl(('德勤', '德勤中国'), case_id='111')
