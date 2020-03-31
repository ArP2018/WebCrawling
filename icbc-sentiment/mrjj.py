# encoding: utf-8
# 每经网
# author: Yin Yalin
import threading

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from Entity import Entity
from crawler_base import SentimentCrawler
from selenium.webdriver.support import expected_conditions as ec

from logger import CustomLogging, LogType
from sougou import Sougou
from utils import conv_pub_date, in_date_range


class MRJJ(SentimentCrawler, ):
    def __init__(self):
        super().__init__()
        self.url = 'http://www.nbd.com.cn/'
        self.name = '每经网'

    def crawl_main_page(self, keyword):
        self.driver.set_page_load_timeout(10)
        self.driver.set_script_timeout(10)
        try:
            self.driver.get(self.url)
        except TimeoutException:
            self.driver.execute_script('window.stop();')

        try:
            self.wait.until(ec.presence_of_element_located((By.ID, 'q')))
        except:
            CustomLogging.log_to_file('每经网打开失败', LogType.ERROR)

        self.driver.find_element_by_id('q').click()
        self.driver.find_element_by_id('q').send_keys(keyword + Keys.ENTER)

        return self.crawl_search_results()

    def crawl_search_results(self):
        search_results = []
        self.driver.maximize_window()

        exit_flag = 0
        while True:
            try:
                self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'search-text')))
            except TimeoutException:
                CustomLogging.log_to_file('每经网搜索结果页错误', LogType.ERROR)
                break

            try:
                result_articles = self.driver.find_elements_by_xpath('//ul[@class="search-text mt15"]/li')

                for each_article in result_articles:
                    item = Entity()

                    item.publish_date = each_article.find_element_by_class_name('articleMaterial_meta').text

                    if not in_date_range(conv_pub_date(item.publish_date, 'mrjj'), self.year_range):
                        exit_flag = 1
                        # 跳出for循环
                        break
                    try:
                        item.short_description = each_article.find_element_by_class_name('articleMaterial_depict').text
                    except NoSuchElementException:
                        item.short_description = ''
                    item.title = each_article.find_element_by_class_name('articleMaterial_title').text

                    if item.title in self.titles:
                        continue
                    else:
                        self.titles.append(item.title)

                    item.url = each_article.find_element_by_class_name(
                        'articleMaterial_title').find_element_by_tag_name('a').get_attribute('href')
                    threading.Thread(target=super().download_and_save_item, args=(item,)).start()

                if exit_flag == 1:
                    break
            except NoSuchElementException:
                CustomLogging.log_to_file('没有搜索结果', LogType.INFO)
                break

            try:
                next_page = self.driver.find_element_by_class_name('next').find_element_by_tag_name('a')
                self.driver.get(next_page.get_attribute('href'))
                # next_page.click()
                # time.sleep(2)
            except TimeoutException:
                self.driver.execute_script('window.stop();')
            except NoSuchElementException:
                break

        return search_results

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'class': 'g-articl-text'}).text
            return full_content
        except Exception:
            CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
            pass


class Mrjj_Sougou(Sougou):
    def __init__(self, site):
        super().__init__(site)
        self.name = '每经网'

    def parse_html(self, url, html):
        bs = BeautifulSoup(html, 'lxml')
        try:
            full_content = bs.find('div', attrs={'class': 'g-articl-text'}).text
            return full_content
        except Exception:
            try:
                full_content = bs.find('article').text
                return full_content
            except:
                # CustomLogging.log_to_file('{0}\n'.format(traceback.format_exc()), LogType.ERROR)
                CustomLogging.log_to_file('页面解析错误: {0}|{1}'.format(self.name, url), LogType.ERROR)
                return ''


if __name__ == '__main__':

    # test.start_crawl(('德勤', '德勤中国'), case_id='111')
    with open('test.html', 'rb') as f:
        html = f.read()

    bs = BeautifulSoup(html, 'lxml')
    try:
        full_content = bs.find('div', attrs={'class': 'g-articl-text'}).text
        print(full_content)
    except Exception:
        try:
            full_content = bs.find('article').text
        except:
            print('asdfdsaf')
