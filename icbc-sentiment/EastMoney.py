# encoding: utf-8
# 爬取东方财富网 http://www.eastmoney.com/
# author: Yin Yalin
import re
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


class EastMoney(SentimentCrawler):
    def __init__(self):
        super().__init__()
        self.url = 'http://www.eastmoney.com/'
        self.name = '东方财富网'

    def crawl_main_page(self, keyword):
        self.driver.get(self.url)
        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'code_suggest')))
        except:
            CustomLogging.log_to_file('东方财富网打开失败', LogType.ERROR)

        self.driver.find_element_by_id('code_suggest').clear()
        self.driver.find_element_by_id('code_suggest').send_keys(keyword + Keys.ENTER)

        self.crawl_search_results()

    def crawl_search_results(self):
        search_results = []
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.maximize_window()

        while True:
            try:
                self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'result-cont')))
            except TimeoutException:
                CustomLogging.log_to_file('东方财富网搜索页面加载失败', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_class_name('result-article')

                for each_article in result_articles:
                    item = Entity()
                    item.title = each_article.find_element_by_tag_name('a').text
                    item.url = each_article.find_element_by_tag_name('a').get_attribute('href')
                    item.short_description = each_article.find_element_by_class_name('des').text
                    item.publish_date = each_article.find_element_by_class_name('g').text

                    threading.Thread(target=self.download_and_save_item, args=(each_article,)).start()

            except NoSuchElementException:
                print('没有搜索结果')
                break

            try:
                next_page = self.driver.find_element_by_xpath(
                    '//div[@class="pagination pagination-centered"]//a[contains(text(), "下一页")]')
                self.driver.get(next_page.get_attribute('href'))
                # next_page.click()
            except NoSuchElementException:
                print('已经是最后一页')
                break

        return search_results

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'qmt_content_div'}).text
            return full_content
        except Exception:
            print('parse error', url)
            pass


class EastMoneyFinance(Sougou):
    def __init__(self, site):
        super().__init__(site)
        self.name = '东方财富网财经板块'

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'ContentBody'}).text
            return full_content
        except Exception:
            return ''


class EastMoneyTieba(Sougou):
    def __init__(self, site):
        super().__init__(site)
        self.name = '东方财富网股吧板块'

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'zwconbody'}).text
            return full_content
        except Exception:
            return ''


class EastMoneyBlog(Sougou):
    def __init__(self, site):
        super().__init__(site)
        self.name = '东方财富网博客板块'

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'articleBody'}).text
            return full_content
        except Exception:
            return ''


if __name__ == '__main__':
    test = EastMoney()
    test.start_crawl(('德勤', '德勤中国'), case_id=111)
