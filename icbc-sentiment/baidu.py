# encoding: utf-8
# 搜狗搜索
# author: Yin Yalin
import re
import threading
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

from Entity import Entity
from crawler_base import SentimentCrawler
from selenium.webdriver.support import expected_conditions as ec

from logger import CustomLogging, LogType
from utils import conv_pub_date, in_date_range


class BaiduSearch(SentimentCrawler, ):
    def __init__(self, site):
        super().__init__()
        self.url = 'https://www.baidu.com/gaoji/advanced.html'
        self.site = site

    def crawl_main_page(self, keyword):
        try:
            self.driver.get(self.url)
        except TimeoutException:
            self.driver.execute_script('window.stop();')

        try:
            self.wait.until(ec.presence_of_element_located((By.XPATH, '//input[@value="百度一下"]')))
        except:
            CustomLogging.log_to_file('百度搜索打开失败', LogType.ERROR)

        # 高级设置
        self.driver.find_element_by_name('q2').send_keys(keyword)
        self.driver.find_element_by_name('q6').send_keys(self.site)
        self.driver.find_element_by_name('rn').click()
        self.driver.find_element_by_xpath('//select/option[@value="50"]').click()
        self.driver.find_element_by_xpath('//input[@value="百度一下"]').click()

        return self.crawl_search_results()

    def crawl_search_results(self):
        search_results = []
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.maximize_window()

        while True:
            try:
                self.wait.until(ec.presence_of_element_located((By.ID, 'container')))
            except TimeoutException:
                CustomLogging.log_to_file('百度搜索结果页错误', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_xpath('//div[@class="result c-container "]')

                for each_article in result_articles:
                    item = Entity()
                    try:
                        item.publish_date = each_article.find_element_by_xpath('.//span[contains(@class,"newTimeFactor_before_abs")]').text.replace('-', '')
                    except NoSuchElementException:
                        continue
                    try:
                        article_cont = each_article.find_element_by_class_name('c-abstract')
                    except NoSuchElementException:
                        continue
                    short_description = article_cont.text
                    item.short_description = re.sub(
                        re.compile('[1-9]\d{3}年(0?[1-9]|1[0-2])月(0?[1-9]|[1-2][0-9]|3[0-1])日\s+-'), '',
                        short_description)
                    item.title = each_article.find_element_by_class_name('t').text
                    if self.keyword not in item.short_description and self.keyword not in item.title:
                        continue

                    if not in_date_range(conv_pub_date(item.publish_date, 'baidu'), self.year_range):
                        continue

                    if item.title in self.titles:
                        continue
                    else:
                        self.titles.append(item.title)

                    item.url = each_article.find_element_by_xpath('.//h3[@class="t"]//a').get_attribute(
                        'href')

                    threading.Thread(target=super().download_and_save_item, args=(item,)).start()

            except TimeoutException:
                CustomLogging.log_to_file('没有搜索结果', LogType.INFO)
                break

            try:
                next_page = self.driver.find_element_by_id('page').find_element_by_class_name('n')
                # self.driver.get(next_page.get_attribute('href'))
                next_page.click()
                time.sleep(2)
            except TimeoutException:
                self.driver.execute_script('window.stop();')
            except NoSuchElementException:
                break

        return search_results

    def parse_html(self, url, html):
        pass


if __name__ == '__main__':
    test = CNStock()
    test.start_crawl(('德勤', '德勤中国'), case_id='111')
