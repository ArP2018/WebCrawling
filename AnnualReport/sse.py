import time

import os
from contextlib import closing

import requests
from progressbar import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from settings import PDF_PATH


class SSE(object):
    def __init__(self):
        self.driver = None
        self.url = 'http://www.sse.com.cn/disclosure/listedinfo/regular/'
        self.pdf_base_path = os.path.join(PDF_PATH, 'sse')
        self.pdf_urls = None
        self.wait = None

    def init_driver(self):
        options = Options()
        # options.set_headless()
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        try:
            self.driver.get(self.url)
            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='sse_list_1 list ']//dd")))
            print('webpage loading complete')
        except:
            pass

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def get_pdf_url_by_code(self, code, s_date=None, e_date=None, **kwargs):
        # 判断起始日期,上交所搜索范围不能大于三年
        if s_date and e_date:
            a = time.strptime(s_date, '%Y-%m-%d')
            b = time.strptime(e_date, '%Y-%m-%d')
            if (b.tm_year - a.tm_year) * 12 + (b.tm_mon - a.tm_mon) > 36:
                print('上交所查询只提供日期间隔不超过3年的公告')
                return
        elif s_date and not e_date:
            a = time.strptime(s_date, '%Y-%m-%d')
            b = time.localtime()
            if (b.tm_year - a.tm_year) * 12 + (b.tm_mon - a.tm_mon) > 36:
                print('上交所查询只提供日期间隔不超过3年的公告')
                return
        else:
            pass

        self.driver.find_element_by_id('inputCode').clear()
        self.driver.find_element_by_id('inputCode').send_keys(code)

        if s_date:
            # self.driver.find_element_by_id('start_date').clear()
            self.driver.find_element_by_id('start_date').send_keys(s_date)

        if e_date:
            # self.driver.find_element_by_id('end_date').clear()
            self.driver.find_element_by_id('end_date').send_keys(e_date)

        try:
            # self.driver.find_element_by_id('btnQuery').click()
            self.driver.execute_script('document.getElementById("btnQuery").click();')
            time.sleep(1)
            print('正在搜索公司代码为 {code} 的报告 ...'.format(code=code))
        except:
            print('搜索失败！')

        search_results = self.driver.find_elements_by_xpath("//div[@class='sse_list_1 list ']//a")

        if search_results:
            url_dict = dict()
            for item in search_results:
                # print(item)
                title = item.text.replace(':', '_')
                url = item.get_attribute('href')
                url_dict[title] = url
            self.pdf_urls = url_dict

    # def download_pdf(self):
    #     if self.pdf_urls:
    #         for k, v in self.pdf_urls.items():
    #             if not os.path.exists(self.pdf_base_path):
    #                 os.makedirs(self.pdf_base_path, )
    #             file_path = os.path.join(self.pdf_base_path, k + '.pdf')
    #             with open(file_path, 'wb') as f:
    #                 print('Start downloading report: {report}'.format(report=k))
    #                 resp = requests.get(v, stream=True)
    #                 f.write(resp.content)
    #     else:
    #         print('No pdf was found. ')
    def download_pdf(self):
        if self.pdf_urls:
            for k, v in self.pdf_urls.items():
                if not os.path.exists(self.pdf_base_path):
                    os.makedirs(self.pdf_base_path, )
                file_path = os.path.join(self.pdf_base_path, k + '.pdf')

                with closing(requests.get(v, stream=True)) as response:
                    chunk_size = 1024  # 单次请求最大值
                    content_size = int(response.headers['content-length'])  # 内容体总大小
                    # print(content_size)
                    widgets = ['Progress: ', Percentage(), ' ', Bar(marker='#', left='[', right=']'), ' ', Timer(),
                               ' ', ETA(), ' ', FileTransferSpeed(), ]
                    number_of_chunks = content_size / chunk_size
                    pbar = ProgressBar(widgets=widgets, maxval=number_of_chunks).start()
                    with open(file_path, "wb") as file:
                        i = 0
                        for data in response.iter_content(chunk_size=chunk_size):
                            file.write(data)
                            pbar.update(i)
                            i += 1
                        pbar.finish()
        else:
            print('没有搜索到符合条件的报告！')


if __name__ == '__main__':
    sse = SSE()
    sse.init_driver()
    sse.get_pdf_url_by_code('601601', s_date='2018-01-01')
    sse.download_pdf()
    sse.close_driver()
