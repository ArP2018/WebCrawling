# 爬取人民网 http://www.people.com.cn/
# author: Yin Yalin
import re
import threading
import time
import traceback

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from Entity import Entity
from crawler_base import SentimentCrawler
from selenium.webdriver.support import expected_conditions as ec

from logger import CustomLogging, LogType
from utils import in_date_range, conv_pub_date


class PeopleCN(SentimentCrawler):
    def __init__(self):
        super().__init__()
        self.url = 'http://search.people.com.cn/cnpeople/news/'
        self.name = '人民网'

    def crawl_main_page(self, keyword):
        self.driver.get(self.url)
        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'keyword')))
        except:
            CustomLogging.log_to_file('人民网主页打开失败', LogType.ERROR)

        self.driver.find_element_by_id('keyword').clear()
        self.driver.find_element_by_id('keyword').send_keys(keyword + Keys.ENTER)

        self.crawl_search_results()

    def crawl_search_results(self):
        exit_flag = 0
        index = 0
        while True:
            try:
                self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'fr')))
            except TimeoutException:
                CustomLogging.log_to_file('人民网搜索结果页面加载失败', LogType.ERROR)
                CustomLogging.log_to_file(traceback.format_exc(), LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_xpath('//div[@class="fr w800"]//ul')

                for each_article in result_articles:
                    item = Entity()
                    pub_date = each_article.find_elements_by_tag_name('li')[2].text

                    item.publish_date = re.search(re.compile(
                        '[1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])\s+(20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d'),
                        pub_date).group()

                    if not in_date_range(conv_pub_date(item.publish_date, 'peoplecn'), self.year_range):
                        exit_flag = 1
                        # 跳出for循环
                        break
                    item.title = each_article.find_element_by_tag_name('a').text
                    item.short_description = each_article.find_elements_by_tag_name('li')[1].text
                    if self.keyword not in item.short_description and self.keyword not in item.title:
                        continue

                    item.url = each_article.find_element_by_tag_name('a').get_attribute('href')
                    threading.Thread(target=self.download_and_save_item, args=(item,)).start()

            except NoSuchElementException:
                break

            if exit_flag == 1:
                break

            try:
                next_page = self.driver.find_element_by_xpath(
                    '//div[@class="show_nav_bar"]//a[contains(text(), "下一页")]')
                next_page.click()
                time.sleep(2)
            except NoSuchElementException:
                break

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'rwb_zw'}).text  # rwb_zw
            return full_content
        except Exception:
            try:
                full_content = bs.find('div', attrs={'class': re.compile('(show_text)|(con)|(gray box_text)')})
                return full_content
            except:
                CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
                return


if __name__ == '__main__':
    test = PeopleCN()
    test.start_crawl(('德勤', '德勤中国'), case_id=111)
