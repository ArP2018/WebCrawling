# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class ZhihuuserPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db, mongo_user, mongo_pwd):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_user = mongo_user
        self.mongo_pwd = mongo_pwd

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
            mongo_user=crawler.settings.get('MONGO_USER'),
            mongo_pwd=crawler.settings.get('MONGO_PWD')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db.authenticate(self.mongo_user, self.mongo_pwd)
        self.db['zhihuuser'].update({'url_token':item['url_token']}, {'$set':item}, True)
        return item