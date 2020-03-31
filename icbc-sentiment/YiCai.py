# encoding: utf-8
# 爬取第一财经 https://www.yicai.com/
# author: Yin Yalin
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
from utils import in_date_range, conv_pub_date


class YiCai(SentimentCrawler):
    def __init__(self):
        super().__init__()
        self.url = 'https://www.yicai.com/'
        self.driver.set_page_load_timeout(15)
        self.driver.set_script_timeout(15)
        self.name = '第一财经'

    def crawl_main_page(self, keyword):
        try:
            self.driver.get(self.url)
        except:
            CustomLogging.log_to_file('加载页面过慢，停止加载，继续下一步操作', LogType.INFO)
            self.driver.execute_script('window.stop()')
        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'searchkeys')))
        except:
            CustomLogging.log_to_file('第一财经网页面打开失败', LogType.ERROR)

        self.driver.find_element_by_id('searchkeys').clear()
        self.driver.find_element_by_id('searchkeys').send_keys(keyword + Keys.ENTER)

        self.crawl_search_results()

    def crawl_search_results(self):
        search_results = []

        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'searchlist')))
        except TimeoutException:
            CustomLogging.log_to_file('第一财经网搜索结果页错误', LogType.ERROR)

        exit_flag = 0
        start_index = 0
        while True:
            try:
                self.wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'f-db')))
            except TimeoutException:
                CustomLogging.log_to_file('文章列表加载失败', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_class_name('f-db')

                for each_article in result_articles[start_index:]:
                    item = Entity()
                    item.publish_date = \
                        each_article.find_element_by_class_name('author').find_elements_by_tag_name('span')[
                            -1].text

                    if not in_date_range(conv_pub_date(item.publish_date, 'yicai'), self.year_range):
                        exit_flag = 1
                        # 跳出for循环
                        break
                    item.title = each_article.find_element_by_tag_name('h2').text
                    item.short_description = each_article.find_element_by_tag_name('p').text

                    if self.keyword not in item.title and self.keyword not in item.short_description:
                        continue

                    item.url = each_article.get_attribute('href')
                    threading.Thread(target=self.download_and_save_item, args=(item,)).start()

                if exit_flag == 1:
                    break

            except NoSuchElementException:
                CustomLogging.log_to_file('没有搜索结果', LogType.ERROR)
                pass

            try:
                # next_page = self.wait.until(ec.visibility_of_element_located(
                #     (By.XPATH, '//button[@class="u-btn" and contains(text(), "加载更多内容")]')))
                # next_page = self.driver.find_element_by_xpath('//button[@class="u-btn" and contains(text(), "加载更多内容")]')
                # next_page.click()
                self.driver.execute_script('document.getElementsByClassName("u-btn")[0].click()')
                time.sleep(2)
                start_index += 20
            except TimeoutException:
                CustomLogging.log_to_file('全部页面加载完成', LogType.INFO)
                break

        return search_results

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'class': 'm-txt'}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            return


if __name__ == '__main__':
    test = YiCai()
    # test.start_crawl(('德勤', '德勤中国'), case_id=111)
    test.start_crawl(('阿里巴巴中国',), case_id=111)
