import os
from contextlib import closing

import requests
import time

import sys
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

crawler_mapping = {
    'sse': ('crawler_sse', 'SSE'),
    'szse': ('crawler_szse', 'SZSE')
}


class GeneralCrawler(object):
    def __init__(self, website):
        print('正在准备连接网站！')
        self.driver = self.__init_driver()
        cls_module = crawler_mapping.get(website, None)
        if cls_module:
            m = __import__(cls_module[0])
            c = getattr(m, cls_module[1])
            self.crawler = c(self.driver)
        else:
            print('网站参数不正确')
            sys.exit()

    def __init_driver(self):
        options = Options()
        options.add_argument('--log-level=3')
        options.add_argument('--disable-extensions')
        options.add_argument('--headless')

        self.driver = Chrome(options=options, )
        self.driver.maximize_window()
        # self.driver.execute_script("document.body.style.zoom='100%';")

        return self.driver

    def __close_driver(self):
        if self.driver:
            self.driver.quit()

    def download_pdf(self, code, keyword=None, s_date=None, e_date=None, **kwargs):
        self.crawler.load_main_page()
        pdf_urls = self.crawler.get_pdf_urls(code, keyword=keyword, s_date=s_date, e_date=e_date, **kwargs)
        self.__close_driver()

        if pdf_urls:
            pdf_base_path = self.crawler.pdf_base_path
            if not os.path.exists(pdf_base_path):
                os.makedirs(pdf_base_path)

            chunk_size = 1024
            # 挨个下载pdf
            print('一共搜索到%s个结果' % len(pdf_urls))
            i = 0
            for k, v in pdf_urls.items():
                try:
                    file_path = os.path.join(pdf_base_path, k + '.pdf')
                    with closing(requests.get(v, stream=True)) as response:
                        file_size = int(response.headers['content-length'])  # 文件大小
                        if (k + '.pdf') in os.listdir(pdf_base_path) and os.path.getsize(file_path) == file_size:
                            print('文件[ %s ] 已经存在' % file_path)
                            continue

                        with open(file_path, 'wb') as file:
                            pbar = tqdm(unit='B', total=file_size, desc=k[:25]+('', '...')[int(len(k)>25)], unit_scale=True, ncols=80)
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                pbar.update(len(chunk))
                                file.write(chunk)
                            pbar.close()
                    i += 1
                except:
                    print('文件 %s.pdf 下载失败' % k)
            if i > 0:
                print('下载完毕，文件存放路径：%s' % pdf_base_path)
        else:
            print('没有搜索到符合条件的pdf！')


if __name__ == '__main__':
    crawler = GeneralCrawler('szse')
    crawler.download_pdf('000002', s_date='2018-04-01', )
