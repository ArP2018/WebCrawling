# encoding: utf-8
# 搜狗搜索
# author: Yin Yalin
import re
import threading
import time
import urllib.parse

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from Entity import Entity
from crawler_base import SentimentCrawler
from selenium.webdriver.support import expected_conditions as ec

from logger import CustomLogging, LogType
from utils import conv_pub_date, in_date_range, format_sougou_date


class Sougou(SentimentCrawler, ):
    def __init__(self, site):
        super().__init__()
        self.url = 'https://www.sogou.com/'
        self.site = site

    def crawl_main_page(self, keyword):
        try:
            self.driver.get(self.url)
        except TimeoutException:
            self.driver.execute_script('window.stop();')

        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'query')))
        except:
            CustomLogging.log_to_file('搜狗搜索打开失败', LogType.ERROR)

        # 高级设置
        elem = self.driver.find_element_by_id('settings')
        ActionChains(self.driver).move_to_element(elem).perform()
        time.sleep(1)
        self.driver.find_element_by_id('advanced-search').click()

        self.driver.find_element_by_xpath('//input[@name="q"]').send_keys(keyword)
        self.driver.find_element_by_xpath('//input[@name="sitequery"]').send_keys(self.site)
        self.driver.find_element_by_xpath('//a[@uigs-id="adv_time-sort"]').click()
        self.driver.find_element_by_xpath('//input[@id="adv-search-btn"]').click()
        # search_keyword = '{0} site:{1}'.format(keyword, self.site)
        # self.driver.find_element_by_id('query').click()
        # self.driver.find_element_by_id('query').send_keys(search_keyword + Keys.ENTER)

        return self.crawl_search_results()

    def crawl_search_results(self):
        search_results = []
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.maximize_window()

        exit_flag = 0
        while True:
            try:
                self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'results')))
            except TimeoutException:
                CustomLogging.log_to_file('每经网搜索结果页错误', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_xpath(
                    '//div[@class="results"]/div[@class="rb" or @class="vrwrap"]')

                for each_article in result_articles[1:]:
                    item = Entity()

                    item.publish_date = format_sougou_date(
                        each_article.find_element_by_xpath('.//cite[contains(@id,"cacheresult_info_")]').text)
                    if each_article.get_attribute('class') == 'rb':
                        try:
                            article_cont = each_article.find_element_by_xpath(
                                './/div[contains(@id, "cacheresult_summary_")]')
                        except NoSuchElementException:
                            continue
                        short_description = article_cont.text
                        item.short_description = re.sub(
                            re.compile('[1-9]\d{3}年(0?[1-9]|1[0-2])月(0?[1-9]|[1-2][0-9]|3[0-1])日\s+-'), '',
                            short_description)
                        item.title = each_article.find_element_by_xpath('.//a[contains(@id, "uigs_")]').text
                        if self.keyword not in item.short_description and self.keyword not in item.title:
                            continue

                        if item.publish_date == '':
                            try:
                                publish_date = each_article.find_element_by_xpath(
                                    './/div[contains(@id, "cacheresult_summary_")]/span').text
                                item.publish_date = publish_date.replace('年', '-').replace('月', '-').replace('日',
                                                                                                             '').replace(
                                    '-', '')
                            except NoSuchElementException:
                                continue
                    else:
                        item.title = each_article.find_element_by_class_name('vrTitle').text
                        try:
                            short_description = each_article.find_element_by_class_name('str_info').text
                        except NoSuchElementException:
                            continue
                        item.short_description = re.sub(
                            re.compile('[1-9]\d{3}年(0?[1-9]|1[0-2])月(0?[1-9]|[1-2][0-9]|3[0-1])日\s+-'), '',
                            short_description)

                        if self.keyword not in item.short_description and self.keyword not in item.title:
                            continue

                        if item.publish_date == '':
                            try:
                                publish_date = each_article.find_element_by_class_name('gray-color').text
                                item.publish_date = publish_date.replace('-', '').replace('年', '-').replace('月',
                                                                                                            '-').replace(
                                    '日', '')
                            except NoSuchElementException:
                                continue

                    if not in_date_range(conv_pub_date(item.publish_date, 'sougou'), self.year_range):
                        exit_flag = 1
                        break

                    if item.title in self.titles:
                        continue
                    else:
                        self.titles.append(item.title)

                    url = each_article.find_element_by_xpath('.//a[contains(@id, "sogou_snapshot_")]').get_attribute(
                        'href')
                    item.url = urllib.parse.unquote(url.split('&')[1].replace('url=', ''))

                    threading.Thread(target=super().download_and_save_item, args=(item,)).start()
                if exit_flag == 1:
                    break

            except TimeoutException:
                CustomLogging.log_to_file('没有搜索结果', LogType.INFO)
                break

            try:
                next_page = self.driver.find_element_by_id('sogou_next')
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
