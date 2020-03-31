import datetime

import pymysql

db = pymysql.connect("10.13.38.20", "webcrawler", "fd909d69c7b164406f59", "scp")
cur = db.cursor()

import xlrd
wb = xlrd.open_workbook('20190225.xlsx')
ws = wb.sheet_by_index(0)

values = []
for r in range(1, ws.nrows):
    print(ws.cell_value(r, 0))
    cell_value = ws.cell_value(r, 0)

    cur.execute('select count(1) from autocrawl_distributor where shortname = "{0}"'.format(cell_value))

    cnt = cur.fetchall()[0][0]
    if cnt > 0:
        cur.execute('update autocrawl_distributor set isused = 1 where shortname = "{0}"'.format(cell_value))
        db.commit()
    else:
        values.append([cell_value, cell_value, datetime.datetime.now(), datetime.datetime.now(), 1, '', 0])


sql = 'insert into autocrawl_distributor values(%s, %s, %s, %s, %s, %s, %s)'
cur.executemany(sql, values)
db.commit()
db.close()