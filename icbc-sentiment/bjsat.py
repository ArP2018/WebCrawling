# encoding: utf-8
# 中国证券网爬虫
# author: Yin Yalin
import datetime
import re
import threading

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By

from Entity import Entity
from crawler_base import SentimentCrawler
from selenium.webdriver.support import expected_conditions as ec

from logger import CustomLogging, LogType


class BJSAT(SentimentCrawler):
    def __init__(self):
        super().__init__()
        self.url = ''
        self.name = '北京税务局'

    def crawl_main_page(self, keyword):
        begin_date = r'{0}/{1}/{2}'.format(datetime.datetime.now().year - self.year_range,
                                           datetime.datetime.now().month,
                                           datetime.datetime.now().day)
        end_date = r'{0}/{1}/{2}'.format(datetime.datetime.now().year, datetime.datetime.now().month,
                                         datetime.datetime.now().day)

        self.url = r'http://www.bjsat.gov.cn/was5/web/search?channelid=255299&sw={0}&orderby=&type=&resultType=&timeRange={1}%E2%80%94{2}&page={3}'.format(
            self.keyword, begin_date, end_date, 1)
        self.driver.get(self.url)

        return self.crawl_search_results()

    def crawl_search_results(self):
        # r = requests.get(self.url)
        # if r.text:
        #     soup = BeautifulSoup(r.text, 'lxml')

        search_results = []
        # self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.maximize_window()

        exit_flag = 0
        while True:
            try:
                self.wait.until(ec.presence_of_element_located((By.ID, 'idData')))
            except TimeoutException:
                CustomLogging.log_to_file('搜索结果出错', LogType.ERROR)
                break
            total_page_num_list = self.driver.find_element_by_class_name("qianm").text.split(' ')
            total_page_num = int(re.sub('\D', '', total_page_num_list[1].strip()))

            if total_page_num == 0:
                CustomLogging.log_to_file("no matches found!!", LogType.INFO)
                break

            try:
                result_articles = self.driver.find_elements_by_xpath('//div[@id="idData"]/li')

                for each_article in result_articles:
                    item = Entity()

                    item.publish_date = each_article.find_elements_by_tag_name('span')[-1].text

                    item.short_description = each_article.find_element_by_class_name(
                        'search_text_content').text.replace('\'', '')
                    item.title = each_article.find_element_by_class_name('search_text_tit').text.replace('\'', '')

                    if self.keyword not in item.short_description and self.keyword not in item.title:
                        continue

                    if item.title in self.titles:
                        continue
                    else:
                        self.titles.append(item.title)

                    item.url = each_article.find_element_by_tag_name('a').get_attribute("href")
                    threading.Thread(target=super().download_and_save_item, args=(item,)).start()

            except NoSuchElementException:
                CustomLogging.log_to_file('没有搜索结果', LogType.INFO)
                break

            try:
                next_page = self.driver.find_element_by_xpath('//div[@class="houm"]/a[contains(text(),"下一页")]')
                next_page_url = next_page.get_attribute('href')
                if next_page_url:
                    self.driver.get(next_page_url)
                else:
                    CustomLogging.log_to_file('完成所有页面爬取', LogType.INFO)
                    break
                # next_page.click()
            except NoSuchElementException:
                break

        return search_results

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'tax_content'}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            pass


if __name__ == '__main__':
    test = CNStock()
    test.start_crawl(('德勤', '德勤中国'), case_id='111')
