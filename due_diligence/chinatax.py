import time

import pymysql
from selenium.webdriver import Chrome, Firefox

from selenium.webdriver.chrome.options import Options

url = 'http://hd.chinatax.gov.cn/xxk/'
db = pymysql.connect("localhost", "root", "1234.abcd", "bi")
cur = db.cursor()

sql = 'SELECT touzi_firm_name FROM bi.touzi_info where touzi_firm_name not in (select comp_name from bi.shuishouweifa)'
sql_01 = 'insert into shuishouweifa(comp_name) values(%s)'
insert_sql = 'insert into shuishouweifa(comp_name, url) values(%s, %s)'
cur.execute(sql)
# options.add_argument('--headless')
options = Options()
driver = Chrome(options=options, executable_path='driver/chromedriver.exe')
# driver = Firefox(executable_path='driver/geckodriver.exe')
firms = [f[0] for f in cur.fetchall()]
for idx, firm in enumerate(firms):
    if idx > 0 and idx % 8 == 0:
        driver.quit()
        time.sleep(1)
        driver = Chrome(options=options, executable_path='driver/chromedriver.exe')
        # driver = Firefox(executable_path='driver/geckodriver.exe')

    driver.get(url)
    input = driver.find_element_by_id('queryvalue')
    input.send_keys(firm)
    driver.execute_script('dosearch();')
    time.sleep(2)
    driver.switch_to.frame('rightiframe')
    a_tags = [td.find_element_by_tag_name('a') for td in
              driver.find_elements_by_tag_name('table')[1].find_elements_by_tag_name('td')[1:]]
    print('正在查询: ' + firm)
    for a in a_tags:
        item_url = a.get_attribute('href')
        title = a.text

        print(title, item_url)
        print('--' * 50)

        cur.execute(insert_sql, (title, item_url))
        db.commit()
    cur.execute(sql_01, firm)
    db.commit()
    driver.switch_to.default_content()

time.sleep(5)
driver.quit()
