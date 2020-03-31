# encoding: utf-8
# 搜狐财经
# author: Yin Yalin
from bs4 import BeautifulSoup

from logger import CustomLogging, LogType
from sougou import Sougou


class SouhuFin(Sougou):
    def __init__(self, site):
        super().__init__(site)
        self.name = '搜狐财经'

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'contentText'}).text
            return full_content
        except Exception:
            try:
                full_content = bs.find('article', attrs={'class': 'article'}).text
                return full_content
            except Exception:
                CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)


if __name__ == '__main__':
    pass
