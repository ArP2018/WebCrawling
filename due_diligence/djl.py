# 点击律
import random
import re
import time
import traceback

import pymysql
import requests
from bs4 import BeautifulSoup

URL = 'http://www.51djl.com/enterprise/judge'
COOKIE = 'ruri=2bc05308-0d83-4190-81f2-83e47b6dc754-c9a64e37-85f9-4c55-b4c5-ce7f94ae2847; UM_distinctid=169a4268cb62-0bcdccae437724-675c772b-144600-169a4268cb7467; CNZZDATA1258139872=1835552072-1553236495-null%7C1553236495; i=114117479017480192; u=%E5%B0%B9%E9%BB%98; r=0; v=0; t=eyJraWQiOiJqd2siLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJhdXRoLjUxZGpsLmNvbSIsImF1ZCI6IjExNDExNzQ3OTAxNzQ4MDE5MiIsImV4cCI6MTU1MzI4MDUwOCwianRpIjoiYVptdVltSGE3bE1GeTNhdlpRdW1xUSIsImlhdCI6MTU1MzIzNzMwOCwic3ViIjoic3ViamVjdCIsImFwcCI6IndlYiJ9.3GL2Kg6PNBKNQnNwCwf29G_S_gcXgxXNY8IYJPNuJExJUjMo3TTFv67p9r6lvuJZrMKz5Dp-Mb_vx7TjxB2kXg'
HEADER = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
    'host': 'www.51djl.com',
    'referer': 'http://www.51djl.com/enterprise/query',
    'cookie': COOKIE
}

db = pymysql.connect("localhost", "root", "1234.abcd", "bis")
cur = db.cursor()

# cur.execute('select firm_id, firm_name from bis.v_valid_firms')
cur.execute('''select firm_id, firm_name from bis.firm_info where firm_id not in (select distinct firm_id from bis.v_valid_firms)
''')
for firm_id, firm_name in cur.fetchall():
    try:
        print('--' * 50)
        print('查询企业 : ' + firm_name)
        time.sleep(2 + random.random())
        resp = requests.post(URL, data={'enterpriseName': firm_name}, headers=HEADER).json()
        results_list = resp.get('info')

        if len(results_list) > 1:
            for r in results_list:
                cur.execute('insert into unmatch values(%s, %s, %s, %s, %s)', (firm_id, firm_name, r.get('k'), r.get('v'), '111'))
                db.commit()
        elif len(results_list) == 1:
            firm_key = results_list[0].get('k')

            time.sleep(random.random() + 2.5)
            resp = requests.get('http://www.51djl.com/enterprise/' + firm_key, headers=HEADER)
            soup = BeautifulSoup(resp.text, 'lxml')

            encryptID = \
                re.findall(re.compile('可以查看(\S*)的涉案金额'), soup.find('meta', attrs={'name': 'description'}).attrs['content'])[
                    0]

            case_json = requests.post('http://www.51djl.com/enterprise/credit/caseSummary',
                                      data={'enterpriseName': encryptID},
                                      headers=HEADER).json()

            print('被告案件总数: ' + str(case_json.get('info').get('defendantCaseAmount')))
            cases = case_json.get('info').get('caseInfos')
            for case in cases:
                role = case.get('role')
                if role == 1:
                    caseCode = case.get('caseCode')
                    caseCourt = case.get('caseCourt')
                    caseDate = case.get('caseDate')
                    caseId = case.get('caseId')
                    caseTitle = case.get('caseTitle')
                    category = case.get('category')
                    url = 'http://www.51djl.com/document/' + case.get('uri')
                    amount = case.get('amount')

                    case_info = (firm_id, caseCode, caseCourt, caseDate, caseId, caseTitle, category, url, amount)
                    cur.execute('insert into djl_wenshu values(%s, %s, %s, %s, %s, %s, %s, %s, %s)', case_info)
                    db.commit()
        else:
            pass
    except:
        print(traceback.format_exc())

db.close()
