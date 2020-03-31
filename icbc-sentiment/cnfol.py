# encoding: utf-8
# 中金在线 http://www.cnfol.com/
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
from utils import conv_pub_date, in_date_range


class CNFOL(SentimentCrawler):
    def __init__(self):
        super().__init__()
        self.url = 'http://so.cnfol.com/'
        self.name = '中金在线'

    def crawl_main_page(self, keyword):
        self.driver.set_page_load_timeout(10)
        try:
            self.driver.get(self.url)
        except TimeoutException:
            self.driver.execute_script('window.stop();')

        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'search-box')))
        except:
            CustomLogging.log_to_file('中金在线网页打开失败', LogType.ERROR)

        self.driver.find_element_by_id('search-box').click()
        self.driver.find_element_by_id('search-box').send_keys(keyword+Keys.ENTER)
        # self.driver.find_element_by_xpath('//a[contains(text(), "搜资讯")]').click()

        return self.crawl_search_results()

    def crawl_search_results(self):
        search_results = []
        self.driver.maximize_window()

        try:
            self.driver.find_element_by_xpath('//dl[@id="flt-sort"]//dd[contains(text(),"按时间排序")]').click()
        except NoSuchElementException:
            pass

        page_index = 1
        while True:
            if page_index > 100:
                break

            try:
                self.wait.until(ec.presence_of_element_located((By.ID, 'results')))
            except TimeoutException:
                CustomLogging.log_to_file('中金在线网搜索结果页错误', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_class_name('result')

                for each_article in result_articles:
                    item = Entity()

                    publish_date = each_article.find_element_by_class_name('c-showurl').text
                    item.publish_date = re.search(re.compile(
                        '[1-9]\d{3}-([1-9]|1[0-2])-([1-9]|[1-2][0-9]|3[0-1])'),
                        publish_date).group()

                    if not in_date_range(conv_pub_date(item.publish_date, 'cnfol'), self.year_range):
                        continue

                    item.short_description = each_article.find_element_by_class_name('c-abstract').text
                    item.title = each_article.find_element_by_class_name('c-title').text
                    if self.keyword not in item.short_description and self.keyword not in item.title:
                        continue

                    if item.title in self.titles:
                        continue
                    else:
                        self.titles.append(item.title)

                    item.url = each_article.find_element_by_class_name('c-title').find_element_by_tag_name(
                        'a').get_attribute('href')
                    threading.Thread(target=super().download_and_save_item, args=(item,)).start()

            except NoSuchElementException:
                CustomLogging.log_to_file('没有搜索结果', LogType.INFO)
                break

            try:
                next_page = self.driver.find_element_by_xpath(
                    '//div[@id="pageFooter"]//a[contains(text(), "下一页")]')
                self.driver.get(next_page.get_attribute('href'))
                # next_page.click()
                page_index += 1
            except NoSuchElementException:
                break

        return search_results

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': re.compile(
                '(__content)|(ArtMainBox)|(Content)')}).text
            return full_content
        except Exception:
            try:
                full_content = bs.find('div', attrs={'class': re.compile('(Article)|(ArtMainArea)')}).text
                return full_content
            except:
                CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
                pass


if __name__ == '__main__':
    test = CNStock()
    test.start_crawl(('德勤', '德勤中国'), case_id='111')
