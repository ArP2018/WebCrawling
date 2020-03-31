# encoding: utf-8
# 北京工商局爬虫
# author: Yin Yalin
import re
import threading

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

from Entity import Entity
from crawler_base import SentimentCrawler
from selenium.webdriver.support import expected_conditions as ec

from logger import CustomLogging, LogType
from utils import conv_pub_date, in_date_range


class BJGSJ(SentimentCrawler):
    def __init__(self):
        super().__init__()
        self.url = 'http://gsj.beijing.gov.cn/'
        self.name = '北京工商局'

    def crawl_main_page(self, keyword):
        self.driver.set_page_load_timeout(10)
        try:
            self.driver.get(self.url)
        except TimeoutException:
            self.driver.execute_script('window.stop();')

        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'searchKey')))
        except:
            CustomLogging.log_to_file('北京工商局网站打开失败', LogType.ERROR)

        self.driver.find_element_by_id('searchKey').click()
        self.driver.find_element_by_id('searchKey').send_keys(keyword)
        self.driver.find_element_by_xpath('//span[contains(text(), "我要搜索")]').click()

        return self.crawl_search_results()

    def crawl_search_results(self):
        search_results = []
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.maximize_window()

        exit_flag = 0
        while True:
            try:
                self.wait.until(ec.presence_of_all_elements_located((By.XPATH, '//div[@class="content"]//div')))
            except TimeoutException:
                CustomLogging.log_to_file('搜索结果出错', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_xpath('//div[@class="content"]//div[@class="news"]')

                for each_article in result_articles:
                    item = Entity()

                    publish_date = each_article.find_element_by_id('essaypubtime').text
                    item.publish_date = re.search(re.compile(
                        '[1-9]\d{3}.(0[1-9]|1[0-2]).(0[1-9]|[1-2][0-9]|3[0-1])\s+(20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d'),
                        publish_date).group()

                    if not in_date_range(conv_pub_date(item.publish_date, 'bjgsj'), self.year_range):
                        exit_flag = 1
                        # 跳出for循环
                        break
                    item.short_description = each_article.find_element_by_id('essaycontent').text
                    item.title = each_article.find_element_by_id('essaytitlelinks').text

                    if self.keyword not in item.short_description and self.keyword not in item.title:
                        continue

                    if item.title in self.titles:
                        continue
                    else:
                        self.titles.append(item.title)

                    item.url = each_article.find_element_by_xpath('.//li[@id="essaytitlelinks"]/a').get_attribute(
                        "href")
                    threading.Thread(target=super().download_and_save_item, args=(item,)).start()

                if exit_flag == 1:
                    break
            except NoSuchElementException:
                CustomLogging.log_to_file('没有搜索结果', LogType.INFO)
                break

            try:
                next_page = self.driver.find_element_by_class_name('next-page')
                self.driver.get(next_page.get_attribute('href'))
                # next_page.click()
            except NoSuchElementException:
                break

        return search_results

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'div_zhengwen'}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            pass


if __name__ == '__main__':
    test = CNStock()
    test.start_crawl(('德勤', '德勤中国'), case_id='111')
