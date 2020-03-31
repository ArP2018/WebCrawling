import time

import pymysql
from selenium.webdriver import Chrome, Firefox, ActionChains

from selenium.webdriver.chrome.options import Options

db = pymysql.connect("localhost", "root", "1234.abcd", "bis")
cur = db.cursor()

sql = 'SELECT firm_id, url FROM bis.beizhixingren where content is null'
cur.execute(sql)
# options.add_argument('--headless')
options = Options()
driver = Chrome(options=options, executable_path='driver/chromedriver.exe')
# driver = Firefox(executable_path='driver/geckodriver.exe')
# firms = [f[0] for f in cur.fetchall()]
firms = cur.fetchall()
for id, url in firms:

    # firm_id, url = firm
    driver.get('https://www.qichacha.com/csusong_{0}.html'.format(id))
    time.sleep(60)
    # susong = driver.find_element_by_id('susong_title')
    # action = ActionChains(driver)
    # action.move_to_element(susong)
    # driver.find_element_by_xpath('.//a[@data-pos="zhixinglist"]').click()
    #
    tab = driver.find_element_by_id('zhixinglist').find_element_by_tag_name('table')
    trs = tab.find_elements_by_tag_name('tr')[2:]
    for tr in trs:
        if tr.text:
            tds = tr.find_elements_by_tag_name('td')
            content = tds[1].text
            punish_date = tds[2].text
            amount = tds[4].text

            cur.execute('update bis.beizhixingren set content = %s, punish_date = %s, amount = %s where firm_id = %s',
                        (
                            content, punish_date, amount, id
                        ))
            db.commit()

    # while True:
    #     a = driver.find_element_by_id('zhixinglist').find_element_by_xpath('.//a[text()=">"]')
    #     if a:
    #         a.click()
    #
    #         time.sleep(2)
    #         tab = driver.find_element_by_id('zhixinglist').find_element_by_tag_name('table')
    #         trs = tab.find_elements_by_tag_name('tr')[2:]
    #         for tr in trs:
    #             if tr.text:
    #                 tds = tr.find_elements_by_tag_name('td')
    #                 content = tds[1].text
    #                 punish_date = tds[2].text
    #                 amount = tds[4].text
    #
    #                 cur.execute(
    #                     'update bis.beizhixingren set content = %s, punish_date = %s, amount = %s where firm_id = %s',
    #                     (
    #                         content, punish_date, amount, id
    #                     ))
    #                 db.commit()
    #
    #     else:
    #         break

driver.quit()
