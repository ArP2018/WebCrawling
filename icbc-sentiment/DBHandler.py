import sqlite3
import Entity


class DBHandler(object):
    def __init__(self):
        self.conn = self.create_conn()
        self.init_table()
        pass

    def create_conn(self):
        conn = sqlite3.connect('rawdata.db')
        return conn

    def init_table(self, ):
        try:
            create_tb_cmd = 'CREATE TABLE IF NOT EXISTS sentiment(case_id,url,title,short_description,publish_date,full_content);'
            self.conn.execute(create_tb_cmd)
            self.conn.commit()
        except:
            print("Create table failed")
            return False

    def save_article_info(self, item: Entity, case_id, ):
        sql = 'insert into sentiment(case_id,url,title,short_description,publish_date,full_content) values (?, ?, ?, ?, ?, ?)'
        cur = self.conn.cursor()
        cur.execute(sql, (case_id, item.url, item.title, item.short_description, item.publish_date, item.full_content))
        cur.close()
        self.conn.commit()

    def close_conn(self):
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    entity = Entity.Entity()

    entity.title = "14'4455"
    entity.short_description = '43:21'
    entity.publish_date = '1'
    entity.full_content = '341'
    entity.url = '388%888/88333'

    db = DBHandler()
    db.save_article_info(entity, '44', )
