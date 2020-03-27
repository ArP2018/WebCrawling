import time
from contextlib import closing

from progressbar import *
import os

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from settings import PDF_PATH


class SZSE(object):
    def __init__(self):
        self.driver = None
        self.url = 'http://disclosure.szse.cn/m/drgg.htm'
        self.pdf_base_path = os.path.join(PDF_PATH, 'szse')
        self.pdf_urls = dict()
        self.wait = None

    def init_driver(self):
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 15)
        try:
            print('connecting website ...')
            self.driver.get(self.url)
            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='index']//table")))
            print('webpage loading complete')
        except:
            print('connection failed!')
            pass

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def get_pdf_url_by_code(self, code, keyword=None, s_date=None, e_date=None):
        self.driver.find_element_by_id('stockCode').clear()
        self.driver.find_element_by_id('stockCode').send_keys(code)

        if keyword:
            self.driver.find_element_by_id('search').clear()
            self.driver.find_element_by_id('search').send_keys(keyword)

        if s_date:
            # 判断起始日期,深交所不支持搜索2001年以前
            if time.strptime(s_date, '%Y-%m-%d').tm_year < 2001:
                print("don't support searching before 2001")
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
            print('website is searching reports for code {code} ...'.format(code=code))
        except:
            print('query error')

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

    # def download_pdf(self):
    #     if self.pdf_urls:
    #         for k, v in self.pdf_urls.items():
    #             if not os.path.exists(self.pdf_base_path):
    #                 os.makedirs(self.pdf_base_path, )
    #             # print(k, v)
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
                    widgets = ['%s.pdf: ' % k, Percentage(), ' ', Bar(marker='█', left='[', right=']'), ' ',DataSize(), ' ', FileTransferSpeed(), ]
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
    s = time.time()
    sse = SZSE()
    sse.init_driver()
    sse.get_pdf_url_by_code('000004', s_date='2018-01-01', e_date='2018-05-01')
    sse.download_pdf()
    sse.close_driver()
    e = time.time()
    print('time elasped: %ss' % str(int(e - s)))
