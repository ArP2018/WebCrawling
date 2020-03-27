import time

import sys
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from settings import PDF_PATH


class SZSE(object):
    def __init__(self, driver):
        self.url = 'http://disclosure.szse.cn/m/drgg.htm'
        self.pdf_base_path = os.path.join(PDF_PATH, 'szse')
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)
        self.pdf_urls = dict()

    def load_main_page(self):
        try:
            self.driver.get(self.url)
            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='index']//table")))
            print('深交所页面加载成功！')
        except:
            print('深交所页面加载失败!')
            sys.exit()

    def get_pdf_urls(self, code, keyword=None, s_date=None, e_date=None, **kwargs):
        self.driver.find_element_by_id('stockCode').clear()
        self.driver.find_element_by_id('stockCode').send_keys(code)

        if keyword:
            self.driver.find_element_by_id('search').clear()
            self.driver.find_element_by_id('search').send_keys(keyword)

        if s_date:
            # 判断起始日期,深交所不支持搜索2001年以前
            if time.strptime(s_date, '%Y-%m-%d').tm_year < 2001:
                print("深交所暂不提供2001年之前的公告信息查询！")
                return

            self.driver.find_element_by_id('startTime').clear()
            self.driver.find_element_by_id('startTime').send_keys(s_date)

        if e_date:
            self.driver.find_element_by_id('endTime').clear()
            self.driver.find_element_by_id('endTime').send_keys(e_date)

        try:
            # self.driver.find_element_by_id('btnQuery').click()
            self.driver.execute_script('document.getElementsByName("imageField")[0].click();')
            time.sleep(2)
            print('正在搜索公司代码为 {code} 的报告 ...'.format(code=code))
        except:
            print('搜索失败！')

        while True:
            search_results = self.driver.find_elements_by_xpath("//div[@class='index']//a[contains(@href, '.PDF')]")

            if search_results:
                for item in search_results:
                    title = item.text.replace(':', '_').replace('：', '_')
                    url = item.get_attribute('href')
                    self.pdf_urls[title] = url

            pages = self.driver.find_elements_by_xpath("//td[@class='page12']//td")[1].find_elements_by_tag_name(
                'span')

            pages = [p.text for p in pages]
            # print(pages)

            if pages[0] == pages[1]:
                break
            else:
                self.driver.find_elements_by_xpath("//td[@class='page12']//td")[2].find_elements_by_tag_name('a')[
                    1].click()
                # print('searching page {page_num}'.format(page_num=pages[0]+1))
                time.sleep(1)
                self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='index']//table")))

        return self.pdf_urls


if __name__ == '__main__':
    pass
