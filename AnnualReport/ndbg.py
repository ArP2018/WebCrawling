import hashlib
import os
import requests

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from settings import PDF_PATH

# 获取深市主板显示的所有上市公司代码和名字
from selenium.webdriver.chrome.options import Options

from db.sqlite import DBOperator


def get_szmb_name_code(driver):
    td_tags = driver.find_elements_by_tag_name('td')

    code_name_dict = dict()

    for tag in td_tags:
        try:
            a_tag = tag.find_element_by_tag_name('a')
            href_value = a_tag.get_attribute('href')

            # print(href_value)
            code_name = eval(href_value.lstrip('javascript:go').rstrip(';'))
            code_name_dict[code_name[0]] = code_name[1]

        except:
            pass

    return code_name_dict


# 保存深交所主板所有上市公司列出的年报pdf对应的url
def store_szse_pdf_urls():
    options = Options()
    options.set_headless()
    # options.add_argument('-headless')
    driver = webdriver.Chrome(options=options)
    driver.get('http://disclosure.szse.cn/m/szmb/ndbgqw.htm')

    optr = DBOperator()
    optr.conn_db()

    for k, v in get_szmb_name_code(driver).items():
        driver.get('http://disclosure.szse.cn/m/szmb/ndbgqw_mb.htm?code={code}&name={name}'.format(code=k, name=v))

        a_tags = driver.find_element_by_class_name('rightlist').find_elements_by_tag_name('a')
        for a in a_tags:
            href = a.get_attribute('href')
            title = a.text
            print(href, title)
            if not optr.if_url_exists(href):
                url_md5 = hashlib.md5(href.encode('utf-8')).hexdigest()
                optr.insert_by_sql('insert into szse(url, url_md5, title) value(?, ?, ?)', href, url_md5, title)

    optr.close_db()

    driver.quit()


# 保存上交所定期报告页面所有报告pdf对应的url
def store_sse_pdf_urls():
    options = Options()
    # options.set_headless()
    # options.add_argument('-headless')
    driver = webdriver.Chrome(options=options)
    driver.get('http://www.sse.com.cn/disclosure/listedinfo/regular/')

    WebDriverWait(driver, 15).until(lambda x: driver.find_element_by_class_name('pagination').is_displayed())
    total_page_num = driver.find_elements_by_xpath("//ul[@class='pagination']//a")[-2].text
    print('total pages: ' + total_page_num)

    optr = DBOperator()
    optr.conn_db()

    for i in range(1, int(total_page_num) + 1):
        if i > 1:
            next_btn = driver.find_elements_by_xpath("//ul[@class='pagination']//a")[-1]  # 取到 > 按钮
            next_btn.click()

        for item in driver.find_elements_by_xpath("//div[@class='sse_list_1 list ']//a"):
            href = item.get_attribute('href')
            title, code = item.text.split(':')
            print(href, title, code)
            if not optr.if_url_exists(href):
                url_md5 = hashlib.md5(href.encode('utf-8')).hexdigest()
                optr.insert_by_sql('insert into szse(url, url_md5, title, code) values(?, ?, ?, ?)', href, url_md5,
                                   title, code)

    optr.close_db()
    driver.quit()


def download_pdf():
    optr = DBOperator()
    optr.conn_db()
    url_list = optr.get_all_urls()

    for item in url_list:
        title = item[0].replace('：', '-').lstrip('*')
        file_path = PDF_PATH + title + '.pdf'

        if file_path not in os.listdir(PDF_PATH):
            url = item[1]
            resp = requests.get(url)

            with open(file_path, 'wb') as f:
                f.write(resp.content)

    optr.close_db()


if __name__ == '__main__':
    store_sse_pdf_urls()
