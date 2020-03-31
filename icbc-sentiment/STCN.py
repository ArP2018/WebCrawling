# 爬取证券时报 http://www.stcn.com/
# author: Yin Yalin
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


class STCN(SentimentCrawler):
    def __init__(self,):
        super().__init__()
        self.url = 'http://www.stcn.com/'
        self.name = '证券时报网'

    # 从主页进入定位搜索框，搜索关键字并爬取搜索结果
    def crawl_main_page(self, keyword):
        try:
            self.driver.get(self.url)
        except TimeoutException:
            pass

        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'contentInput_0')))
        except:
            CustomLogging.log_to_file('证券时报网页面打开失败，不能定位搜索框元素', LogType.ERROR)

        self.driver.find_element_by_id('contentInput_0').clear()
        self.driver.find_element_by_id('contentInput_0').send_keys(keyword + Keys.ENTER)

        self.crawl_search_results()

    # 爬取搜索结果
    def crawl_search_results(self):
        search_results = []
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.maximize_window()
        try:
            self.wait.until(ec.presence_of_element_located(
                (By.XPATH, '//div[@id="search_result"]//a[contains(text(), "按更新时间排序")]')))
            self.driver.find_element_by_xpath('//div[@id="search_result"]//a[contains(text(), "按更新时间排序")]').click()
        except:
            CustomLogging.log_to_file('证券时报搜索结果页打开失败', LogType.ERROR)

        exit_flag = 0
        page_num = 1
        while True:
            # 搜索结果只会显示100页
            if page_num == 100:
                break

            try:
                self.wait.until(ec.presence_of_element_located((By.ID, 'search_list')))
            except TimeoutException:
                CustomLogging.log_to_file('中国证券网搜索结果页错误', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_xpath('//div[@id="search_list"]//dl')

                for each_article in result_articles:
                    item = Entity()
                    item.publish_date = each_article.find_elements_by_tag_name('dd')[1].find_element_by_tag_name(
                        'span').text
                    # 判断文章是否在指定年限内,如果不在指定年限则退出
                    if not in_date_range(conv_pub_date(item.publish_date, 'STCN'), self.year_range):
                        exit_flag = 1
                        # 跳出for循环
                        break
                    item.short_description = each_article.find_elements_by_tag_name('dd')[0].text
                    item.title = each_article.find_element_by_tag_name('a').text

                    # 关键字过滤,如果关键在在文章标题和简述里都没出现，则判断下一条
                    if self.keyword not in item.short_description and self.keyword not in item.title:
                        continue

                    if item.title in self.titles:
                        continue
                    else:
                        self.titles.append(item.title)

                    item.url = each_article.find_element_by_tag_name('a').get_attribute('href')
                    threading.Thread(target=self.download_and_save_item, args=(item,)).start()

                # 跳出while循环
                if exit_flag == 1:
                    break
            except TimeoutException:
                CustomLogging.log_to_file('中国证券网搜索结果页加载错误', LogType.ERROR)
            try:
                next_page = self.driver.find_element_by_class_name('next')
                next_page.click()
                page_num += 1
            except NoSuchElementException:
                # print('已经是最后一页')
                break

        return search_results

    # 解析web页面的新闻内容
    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'id': 'ctrlfscont'}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            return


if __name__ == '__main__':
    test = STCN()
    test.start_crawl(('德勤', '德勤中国'), case_id='111')
