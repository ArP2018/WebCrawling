import pandas as pd

import pymysql

DB = pymysql.connect("localhost", "root", "1234.abcd", "bis")
CUR = DB.cursor()
CUR.execute('select title, url, wenhao, source,  content from bi.huanbaochufa')

records = CUR.fetchall()

CUR.execute('select chufa_title, source_url, wenhao, source,  content, issue_date from bi.baojianchufa')
bjh_records = CUR.fetchall()

CUR.execute('select title, url, wenshuhao, source,  concat(chufadanwei, weiguineirong), chufariqi, chufajieguo from bi.yinjianchufa')
yjh_records = CUR.fetchall()


CUR.execute('''
select firm_pname, firm_name, relation, percent from bis.v_firm_info where firm_id != ''
''')

info = []
bjh = []
yjh = []
firms = CUR.fetchall()
for firm in firms:
    for r in records:
        content = r[4]
        if firm[1] in content:
            print(firm[0], r[0])
            info.append([firm[0], firm[1], firm[2], firm[3], r[0], r[1], r[2], r[3], r[4]])

    for r in bjh_records:
        content = r[4]
        if firm[0] in content:
            print(firm[0], r[0])
            bjh.append([firm[0], firm[1], firm[2], firm[3], r[0], r[1], r[2], r[3], r[4], r[5]])

    for r in yjh_records:
        content = r[4]
        if firm[0] in content:
            print(firm[0], r[0])
            yjh.append([firm[0], firm[1], firm[2], firm[3], r[0], r[1], r[2], r[3], r[4], r[5], r[6]])
DB.close()

df = pd.DataFrame(info)
df.to_excel('环保处罚.xlsx', index=False)

df = pd.DataFrame(bjh)
df.to_excel('保监会处罚.xlsx', index=False)

df = pd.DataFrame(yjh)
df.to_excel('银监会处罚.xlsx', index=False)