# encoding: utf-8
# 爬取中国经济网 http://www.ce.cn/
# author: Yin Yalin
import threading
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from Entity import Entity
from crawler_base import SentimentCrawler
from selenium.webdriver.support import expected_conditions as ec

from logger import CustomLogging, LogType
from sougou import Sougou


class CE(SentimentCrawler):
    def __init__(self):
        super().__init__()
        self.url = 'http://www.ce.cn/'
        self.name = '中国经济网'

    def crawl_main_page(self, keyword):
        self.driver.get(self.url)
        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'so360_keyword')))
        except:
            CustomLogging.log_to_file('中国经济网主页打开失败', LogType.ERROR)

        self.driver.find_element_by_id('so360_keyword').clear()
        self.driver.find_element_by_id('so360_keyword').send_keys(keyword + Keys.ENTER)

        self.crawl_search_results()

    def crawl_search_results(self):
        search_results = []
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.maximize_window()
        try:
            self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'result')))
        except TimeoutException:
            CustomLogging.log_to_file('中国经济网搜索结果页面加载失败', LogType.ERROR)

        while True:
            try:
                result_articles = self.driver.find_elements_by_class_name('res-list')

                for each_article in result_articles:
                    item = Entity()
                    item.title = each_article.find_element_by_class_name('res-title').text
                    item.url = each_article.find_element_by_tag_name('a').get_attribute('href')
                    try:
                        item.short_description = each_article. \
                            find_element_by_xpath('./div[@class="res-rich so-rich-news clearfix"]//*').text
                        item.publish_date = each_article.find_element_by_class_name('gray').text
                        continue
                    except NoSuchElementException:
                        pass

                    try:
                        item.short_description = each_article.find_element_by_class_name('res-desc').text
                        item.publish_date = ''
                    except NoSuchElementException:
                        item.short_description = ''
                        item.publish_date = ''

                    threading.Thread(target=self.download_and_save_item, args=(item,)).start()

            except NoSuchElementException:
                pass

            return search_results

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'articleText'}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            return

class CE_Sougou(Sougou):
    def __init__(self, site):
        super().__init__(site)
        self.name = '中国经济网'

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'articleText'}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            return


if __name__ == '__main__':
    test = CE()
    # test.start_crawl(('德勤', '德勤中国'), case_id=111)
    test.start_crawl(('德勤',), case_id=111)
