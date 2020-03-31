# encoding: utf-8
# 爬取凤凰财经 https://finance.ifeng.com/
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


class IFengFinance(SentimentCrawler):
    def __init__(self):
        super().__init__()
        self.url = 'https://search.ifeng.com/sofeng/'
        self.name = '凤凰财经'

    def crawl_main_page(self, keyword):
        self.driver.get(self.url)
        try:
            self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'ifengSS')))
        except:
            CustomLogging.log_to_file('凤凰财经网页面打开失败', LogType.ERROR)

        # self.driver.execute_script('document.getElementsByClassName("btn-1NI76BXl clearfix")[0].click()')
        self.driver.find_element_by_class_name('ifengSS').click()

        self.driver.find_element_by_class_name('ifengSS').send_keys(keyword + Keys.ENTER)

        self.crawl_search_results()

    def crawl_search_results(self):
        search_results = []
        # self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.maximize_window()

        while True:
            try:
                self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'mainM')))
            except TimeoutException:
                CustomLogging.log_to_file('凤凰财经网搜索结果页错误', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_class_name('searchResults')

                for each_article in result_articles:
                    item = Entity()

                    publish_date = each_article.find_elements_by_tag_name('p')[2].text
                    item.publish_date = re.search(re.compile(
                        '[1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])\s+(20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d'),
                        publish_date).group()

                    if not in_date_range(conv_pub_date(item.publish_date, 'ifeng'), self.year_range):
                        exit_flag = 1
                        # 跳出for循环
                        continue

                    item.title = each_article.find_element_by_tag_name('a').text
                    item.short_description = each_article.find_elements_by_tag_name('p')[1].text

                    if self.keyword not in item.short_description and self.keyword not in item.title:
                        continue

                    if item.title in self.titles:
                        continue
                    else:
                        self.titles.append(item.title)

                    item.url = each_article.find_element_by_tag_name('a').get_attribute('href')
                    threading.Thread(target=self.download_and_save_item, args=(item,)).start()

            except NoSuchElementException:
                CustomLogging.log_to_file('没有搜索结果', LogType.INFO)
                break

            try:
                next_page = self.driver.find_element_by_xpath(
                    '//div[@class="next0825"]//a[contains(text(), "下一页")]')
                next_page.click()
            except NoSuchElementException:
                break

        return search_results

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'txtBox'}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            pass


if __name__ == '__main__':
    test = IFengFinance()
    test.start_crawl(('德勤', '德勤中国'), case_id=111)
