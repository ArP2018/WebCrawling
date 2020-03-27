'''
Author: Yin, Evan Yalin
Date: 2019-8-10
Purpose: redis database interface
'''

import redis

from settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, VALIDATED_HTTP_KEY, CRAWLED_POOL_KEY, VALIDATED_HTTPS_KEY


class RedisHandler:
    def __init__(self):
        self.conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

    def lpush_crawled_item(self, item, ):
        self.conn.lpush(CRAWLED_POOL_KEY, item)

    def rpop_crawled_item(self):
        return self.conn.rpop(CRAWLED_POOL_KEY)

    def sadd_valid_http_item(self, item):
        self.conn.sadd(VALIDATED_HTTP_KEY, item)

    def sget_valid_http_item(self):
        return self.conn.srandmember(VALIDATED_HTTP_KEY)

    def sadd_valid_https_item(self, item):
        self.conn.sadd(VALIDATED_HTTPS_KEY, item)

    def sget_valid_https_item(self):
        return self.conn.srandmember(VALIDATED_HTTPS_KEY)

    def sget_all_https_item(self):
        return self.conn.smembers(VALIDATED_HTTPS_KEY)

    def sget_all_http_item(self):
        return self.conn.smembers(VALIDATED_HTTP_KEY)

    def sremove_https_item(self, item):
        self.conn.srem(VALIDATED_HTTPS_KEY, item)

    def sremove_http_item(self, item):
        self.conn.srem(VALIDATED_HTTP_KEY, item)

    def llen_crawled_item(self):
        return self.conn.llen(CRAWLED_POOL_KEY)
