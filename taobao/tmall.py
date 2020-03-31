import random
import re
import time
import traceback

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
driver = Chrome(executable_path='./driver/chromedriver.exe', options=options)

driver.get('https://www.tmall.com')

time.sleep(30)
# 洗发水url
url = 'https://list.tmall.com/search_product.htm?s=1200&q=%CF%B4%B7%A2%CB%AE&sort=s&style=g&from=mallfp..pc_1_searchbutton&active=1&spm=a220m.1000858.0.0.424e6208MxC3g7&smAreaId=500100&type=pc#J_Filter'

driver.get(url)

# data_path = './data/product_id_list.csv'
# with open(data_path, 'a') as f:
#     f.write('data_id, sku_id, title' + '\n')
data_path = './data/temp/'

try:
    for i in range(21, 80):
        current_path = data_path + 'page_{0}.csv'.format(str(i))
        with open(current_path, 'a') as f:

            f.write('data_id, sku_id, title' + '\n')

        print('current page: {0}'.format(str(i)))
        soup = BeautifulSoup(driver.page_source, 'lxml')

        product_list = soup.find_all('div', class_='product ')
        for p in product_list:
            product_id = p.attrs['data-id']
            title = p.find('p', class_='productTitle').find('a').attrs['title']
            url = p.find('p', class_='productTitle').find('a').attrs['href'].lstrip('//')
            sku_id = re.findall(re.compile('skuId=(\d*)&'), url)[0]
            shop = p.find('div', class_='productShop').find('a').text
            print(product_id, sku_id, title)

            with open(current_path, 'a') as f:
                f.write('{0}, {1}, {2} \n'.format(product_id, sku_id, title))



        time.sleep(20)

except:
    print(traceback.format_exc())
    driver.save_screenshot('error.png')
