import os

import sys

import time

from settings import PDF_PATH
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class SSE():
    def __init__(self, driver):
        self.url = 'http://www.sse.com.cn/disclosure/listedinfo/regular/'
        self.pdf_base_path = os.path.join(PDF_PATH, 'sse')
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)
        self.pdf_urls = dict()

    def load_main_page(self):
        try:
            self.driver.get(self.url)
            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='sse_list_1 list ']//dd")))
            print('上交所页面加载成功！')
        except:
            print('上交所页面加载失败!')
            sys.exit()

    def get_pdf_urls(self, code, s_date=None, e_date=None, **kwargs):
        self.driver.find_element_by_id('inputCode').clear()
        self.driver.find_element_by_id('inputCode').send_keys(code)

        if s_date:
            # self.driver.find_element_by_id('start_date').clear()
            self.driver.execute_script(
                "var setDate=document.getElementById('start_date');setDate.removeAttribute('readonly');")
            self.driver.find_element_by_id('start_date').send_keys(s_date)

        if e_date:
            # self.driver.find_element_by_id('end_date').clear()
            self.driver.execute_script(
                "var setDate=document.getElementById('end_date');setDate.removeAttribute('readonly');")
            self.driver.find_element_by_id('end_date').send_keys(e_date)

        try:
            # self.driver.find_element_by_id('btnQuery').click()
            self.driver.execute_script('document.getElementById("btnQuery").click();')
            time.sleep(3)
            print('正在搜索公司代码为 {code} 的报告 ...'.format(code=code))
        except:
            print('搜索失败！')

        search_results = self.driver.find_elements_by_xpath("//div[@class='sse_list_1 list ']//dd")

        if search_results:
            url_dict = dict()
            for item in search_results:
                # print(item)
                title = item.find_element_by_tag_name('a').text.replace(':', '_') + '_' + item.find_element_by_tag_name(
                    'span').text
                url_dict[title] = item.find_element_by_tag_name('a').get_attribute('href')
            self.pdf_urls = url_dict
        # print(self.pdf_urls)
        return self.pdf_urls


if __name__ == '__main__':
    pass
