import hashlib
import sqlite3
from settings import DB_PATH


class DBOperator():
    def __init__(self):
        self.conn = None

    def conn_db(self):
        try:
            self.conn = sqlite3.connect(DB_PATH)
            return self.conn
        except:
            return None

    def close_db(self):
        if self.conn is not None:
            self.conn.close()

    def insert_by_sql(self, sql, *args, **kwargs):
        try:
            if self.conn:
                cursor = self.conn.cursor()

                cursor.execute(sql, args)
                cursor.close()

                self.conn.commit()
            else:
                raise sqlite3.Error('no sqllite connection')
        except:
            raise sqlite3.Error('insert error')

    def if_url_exists(self, url):
        try:
            if self.conn:
                cursor = self.conn.cursor()
                url_md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
                res = cursor.execute('select count(url) as url_count from szse where url_md5 = ?', url_md5)

                cursor.close()
                return res
            else:
                raise sqlite3.Error('no sqllite connection')
        except:
            raise sqlite3.Error('query error ')

    def get_all_urls(self):
        try:
            if self.conn:
                cursor = self.conn.cursor()
                cursor.execute('select title, url from szse')
                res = cursor.fetchall()
                cursor.close()
                return res
            else:
                raise sqlite3.Error('no sqllite connection')
        except:
            raise sqlite3.Error('query error ')


if __name__ == '__main__':
    pass
