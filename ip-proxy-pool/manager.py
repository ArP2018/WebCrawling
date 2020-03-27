'''
Author: Yin, Evan Yalin
Date: 2019-8-10
Purpose:
'''

import json

from db import RedisHandler
from utils import Util


class ProxyManager:
    db = RedisHandler()

    def __init__(self):
        pass

    @classmethod
    def feed_pool(cls, item):
        '''
        添加代理ip
        :param item: json字符串
        :return:
        '''
        proxy_item = json.loads(item)
        print('proxy {0}://{1}:{2} added'.format(proxy_item['type'], proxy_item['ip'], proxy_item['port']))
        cls.db.lpush_crawled_item(item)

    @classmethod
    def is_queue_idle(cls):
        '''
        判断redis增量队列是否空闲
        如果队列长度小于10就认为空闲
        :return: True or False
        '''
        q_length = cls.db.llen_crawled_item()
        if q_length <= 10:
            return True
        return False

    @classmethod
    def validate(cls):
        '''
        从爬取的代理列表里逐个验证，验证成功的存入有效代理池
        :return:
        '''
        while True:
            item = cls.db.rpop_crawled_item()

            if item:
                proxy_item = json.loads(item)
                proxy_type = proxy_item['type']
                result = Util.valid_proxy(proxy_item['ip'], proxy_item['port'], proxy_type)

                if result and proxy_type.lower() == 'http':
                    cls.db.sadd_valid_http_item(item)
                elif result and proxy_type.lower() == 'https':
                    cls.db.sadd_valid_https_item(item)
                else:
                    pass
            else:
                break

    @classmethod
    def refresh_proxy_pool(cls):
        '''
        重复验证https和http两个代理池
        :return: 验证报告
        '''
        all_https_proxies = cls.db.sget_all_https_item()
        all_http_proxies = cls.db.sget_all_http_item()

        all_proxies = list(all_https_proxies) + list(all_http_proxies)

        http_total_count, http_abandoned_count = len(all_http_proxies), 0
        https_total_count, https_abandoned_count = len(all_https_proxies), 0
        for item in all_proxies:
            proxy_item = json.loads(item)
            proxy_type = proxy_item['type']

            result = Util.valid_proxy(proxy_item['ip'], proxy_item['port'], proxy_type)

            if not result and proxy_type.lower() == 'http':
                cls.db.sremove_http_item(item)
                http_abandoned_count += 1
            elif not result and proxy_type.lower() == 'https':
                cls.db.sremove_https_item(item)
                https_abandoned_count += 1
            else:
                pass

        validation_report = 'Validation Report: \n' \
                            '{0} proxies are validated, {1} http proxy, {2} https proxy; \n' \
                            '{3} proxies are unavailable and abandoned, {4} http proxy, {5} https proxy; \n' \
                            '{6} proxies are available and remain, {7} http proxy, {8} https proxy.'.format(
            str(http_total_count + https_total_count), str(http_total_count), str(https_total_count),
            str(http_abandoned_count + https_abandoned_count), str(http_abandoned_count), str(https_abandoned_count),
            str(len(all_proxies) - http_abandoned_count - https_abandoned_count),
            str(http_total_count - http_abandoned_count),
            str(https_total_count - https_abandoned_count)
        )

        return validation_report
