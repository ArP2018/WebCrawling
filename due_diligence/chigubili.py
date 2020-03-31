import pymysql

DB = pymysql.connect("localhost", "root", "1234.abcd", "bi")

gudong_sql = 'select gudong, chigubili from bi.gudong_info '
touzi_sql = 'select touzi_firm_name, chuzibili from bi.touzi_info'

import pandas as pd

df = pd.read_excel('11家发行人及股东风险信息.xlsx')

CUR = DB.cursor()
CUR.execute(gudong_sql)

gudong = dict(CUR.fetchall())
CUR.execute(touzi_sql)
touzi = dict(CUR.fetchall())
DB.close()


def replace_gudong(txt):
    try:
        print(gudong[txt])
        return gudong[txt]
    except:
        return ''


def replace_touzi(txt):
    try:
        print(touzi[txt])
        return touzi[txt]
    except:
        return ''


df['持股比例'] = df['事项主体'].apply(replace_gudong)
df['出资比例'] = df['事项主体'].apply(replace_touzi)

df.to_excel('results.xlsx')
