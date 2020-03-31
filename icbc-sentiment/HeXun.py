# encoding: utf-8
# 和讯网文章爬虫 http://www.hexun.com/
# author: Yin Yalin
import re
import threading
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from Entity import Entity
from crawler_base import SentimentCrawler
from selenium.webdriver.support import expected_conditions as ec

from logger import CustomLogging, LogType
from sougou import Sougou
from utils import in_date_range, conv_pub_date


class HeXun(SentimentCrawler):
    def __init__(self):
        super().__init__()
        self.url = 'http://www.hexun.com/'
        self.name = '和讯财经'

    def crawl_main_page(self, keyword):
        self.driver.set_page_load_timeout(5)
        try:
            self.driver.get(self.url)
        except TimeoutException:
            self.driver.execute_script('window.stop()')
        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'textMessage')))
        except:
            CustomLogging.log_to_file('和讯财经网打开失败', LogType.ERROR)

        self.driver.find_element_by_id('textMessage').clear()
        self.driver.find_element_by_id('textMessage').send_keys(keyword + Keys.ENTER)

        return self.crawl_search_results()

    def crawl_search_results(self):
        search_results = []
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.maximize_window()

        # 和讯文章
        try:
            wz_btn = self.driver.find_element_by_xpath('//div[@class="searchRe-top-b"]/a[contains(text(), "文章")]')
            wz_btn.click()



            while True:
                try:
                    result_articles = self.driver.find_elements_by_xpath('//table[@class="stocktab mt6"]//tr')

                    for each_article in result_articles[1:]:
                        item = Entity()
                        item.publish_date = each_article.find_elements_by_tag_name('td')[3].text

                        if not in_date_range(conv_pub_date(item.publish_date, 'hexun'), self.year_range):
                            continue
                        item.title = each_article.find_elements_by_tag_name('td')[1].text
                        item.short_description = each_article.find_elements_by_tag_name('td')[2].text
                        if self.keyword not in item.short_description and self.keyword not in item.title:
                            continue

                        item.url = each_article.find_elements_by_tag_name('td')[1].find_element_by_tag_name(
                            'a').get_attribute('href')
                        threading.Thread(target=self.download_and_save_item, args=(item,)).start()
                except NoSuchElementException:
                    break
                try:
                    next_page = self.driver.find_element_by_xpath('//div[@class="hx_paging"]//a[contains(text(), "下一页")]')
                    next_page_class = self.driver.find_element_by_xpath(
                        '//div[@class="hx_paging"]//a[contains(text(), "下一页")]/..').get_attribute('class')

                    if next_page_class == 'no_next':
                        break

                    next_page.click()
                    time.sleep(2)
                except:
                    break
        except NoSuchElementException:
            pass

        # 和讯新闻
        news_btn = self.driver.find_element_by_xpath('//div[@id="headLayer"]/a[contains(text(), "新闻")]')
        news_btn.click()
        time.sleep(1)
        while True:
            try:
                self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'searchResult')))
            except TimeoutException:
                CustomLogging.log_to_file('和讯财经新闻搜索结果加载失败', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_class_name('newslist-a')

                for each_article in result_articles:
                    item = Entity()
                    item.publish_date = \
                        each_article.find_element_by_class_name('news-l-t').find_elements_by_tag_name('span')[-1].text
                    if not in_date_range(conv_pub_date(item.publish_date, 'hexun_news'), self.year_range):
                        continue

                    item.title = each_article.find_element_by_xpath('.//span[@class="breakdiv"]/a').text
                    item.short_description = each_article.find_element_by_class_name('news-l-c').text
                    if self.keyword not in item.short_description and self.keyword not in item.title:
                        continue

                    item.url = each_article.find_element_by_xpath('.//span[@class="breakdiv"]/a').get_attribute('href')
                    threading.Thread(target=self.download_and_save_item, args=(item,)).start()

            except NoSuchElementException:
                break

            try:
                next_page = self.driver.find_element_by_xpath('//div[@class="hx_paging"]//a[contains(text(), "下一页")]')
                next_page_class = self.driver.find_element_by_xpath(
                    '//div[@class="hx_paging"]//a[contains(text(), "下一页")]/..').get_attribute('class')

                if next_page_class == 'no_next':
                    break

                next_page.click()
                time.sleep(2)
            except:
                break

        # 和讯博客
        news_btn = self.driver.find_element_by_xpath('//div[@class="search-rs-list-ty"]/a[contains(text(), "博客")]')
        news_btn.click()
        self.driver.find_element_by_id('s1_t').click()
        exit_flag = 0
        while True:
            try:
                self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'searchResult')))
            except TimeoutException:
                CustomLogging.log_to_file('和讯财经博客搜索结果加载失败', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_class_name('newslist-a')

                for each_article in result_articles:
                    item = Entity()
                    item.publish_date = \
                        each_article.find_element_by_class_name('news-l-t').find_elements_by_tag_name('span')[
                            -1].text
                    if not in_date_range(conv_pub_date(item.publish_date, 'hexun_blog'), self.year_range):
                        exit_flag = 1
                        break

                    item.title = each_article.find_element_by_xpath('.//span[@class="breakdiv"]/a').text
                    item.short_description = each_article.find_element_by_class_name('news-l-c').text
                    if self.keyword not in item.short_description and self.keyword not in item.title:
                        continue

                    item.url = each_article.find_element_by_xpath('.//span[@class="breakdiv"]/a').get_attribute(
                        'href')
                    threading.Thread(target=self.download_and_save_item, args=(item,)).start()

            except NoSuchElementException:
                break

            if exit_flag == 1:
                break

            try:
                next_page = self.driver.find_element_by_xpath(
                    '//div[@class="hx_paging"]//a[contains(text(), "下一页")]')
                next_page_class = self.driver.find_element_by_xpath(
                    '//div[@class="hx_paging"]//a[contains(text(), "下一页")]/..').get_attribute('class')

                if next_page_class == 'no_next':
                    break

                next_page.click()
                time.sleep(2)
            except:
                break

        return search_results

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'class': re.compile(
                '(ArticleBlogText)|(art_contextBox)|(article)')}).text  # ArticleBlogText  #art_contextBox  #article
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            pass


class HexunSougou(Sougou):
    def __init__(self, site):
        super().__init__(site)
        self.name = '和讯网'

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'class': re.compile(
                '(ArticleBlogText)|(art_contextBox)|(article)')}).text  # ArticleBlogText  #art_contextBox  #article
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            pass


if __name__ == '__main__':
    test = HeXun()
    test.start_crawl(('德勤', '德勤中国'), case_id=111)
