# encoding: utf-8
# 搜狐财经
# author: Yin Yalin
import re

from bs4 import BeautifulSoup

from baidu import BaiduSearch
from logger import CustomLogging, LogType


class TongHuaShun(BaiduSearch):
    def __init__(self, site):
        super().__init__(site)
        self.name = '同花顺'

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        [s.extract() for s in bs('script')]
        try:
            full_content = bs.find('div', attrs={'class': re.compile(
                '(main-text)|(article-con)|(post-detail-text )|(rich_media_content )|(art_main)')}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)


if __name__ == '__main__':
    pass
