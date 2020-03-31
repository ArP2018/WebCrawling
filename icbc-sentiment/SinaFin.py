# encoding: utf-8
# 新浪财经 https://finance.sina.com.cn/
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
from logger import LogType, CustomLogging
from utils import in_date_range, conv_pub_date


class SinaFin(SentimentCrawler):
    def __init__(self):
        super().__init__()
        self.url = 'https://finance.sina.com.cn/'
        self.name = '新浪财经'

    # 从主页进入定位搜索框，搜索关键字并爬取搜索结果
    def crawl_main_page(self, keyword):
        try:
            self.driver.set_page_load_timeout(10)
            self.driver.get(self.url)
        except TimeoutException:
            self.driver.execute_script('window.stop();')
            pass

        try:
            self.driver.find_element_by_class_name('snp-btn-close').click()
        except NoSuchElementException:
            pass

        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'suggest01_input')))
        except:
            CustomLogging.log_to_file('新浪财经页面打开失败', LogType.ERROR)

        # self.driver.find_elements_by_class_name('ds_button')[-1].click()

        self.driver.execute_script('document.getElementsByClassName("ds_button")[1].click();')
        self.driver.find_elements_by_class_name('dsl_cont')[-1].find_element_by_xpath('.//p[contains(text(), "新闻")]').click()

        self.driver.find_element_by_id('suggest01_input').click()
        self.driver.find_element_by_id('suggest01_input').send_keys(keyword + Keys.ENTER)

        self.crawl_search_results()

    # 爬取搜索结果
    def crawl_search_results(self):
        search_results = []
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.maximize_window()
        exit_flag = 0
        while True:
            try:
                self.wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'r-info')))
            except TimeoutException:
                CustomLogging.log_to_file('搜索结果为空', LogType.ERROR)

            result_articles = self.driver.find_elements_by_class_name('r-info')

            for each_article in result_articles:
                item = Entity()
                try:
                    pub_date = each_article.find_element_by_class_name('fgray_time').text
                except NoSuchElementException:
                    continue
                item.publish_date = re.search(re.compile(
                    '[1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])\s+(20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d'),
                    pub_date).group()
                # 判断文章是否在指定年限内,如果不在指定年限则退出
                if not in_date_range(conv_pub_date(item.publish_date, 'sina'), self.year_range):
                    exit_flag = 1
                    # 跳出for循环
                    break
                item.short_description = each_article.find_element_by_class_name('content').text
                item.title = each_article.find_element_by_tag_name('h2').text

                # 关键字过滤,如果关键在在文章标题和简述里都没出现，则判断下一条
                if self.keyword not in item.short_description and self.keyword not in item.title:
                    continue

                if item.title in self.titles:
                    continue
                else:
                    self.titles.append(item.title)

                item.url = each_article.find_element_by_xpath('.//h2/a').get_attribute('href')
                threading.Thread(target=self.download_and_save_item, args=(item,)).start()

            # 跳出while循环
            if exit_flag == 1:
                break

            try:
                next_page = self.driver.find_element_by_xpath('//div[@class="pagebox"]/a[@title="下一页"]')
                # next_page.click()
                self.driver.get(next_page.get_attribute('href'))
                # time.sleep(2)
            except NoSuchElementException:
                # print('已经是最后一页')
                break

        return search_results

    # 解析web页面的新闻内容
    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'artibody'}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            return


if __name__ == '__main__':
    test = SinaFin()
    test.start_crawl(('德勤', '德勤中国'), case_id='111')
