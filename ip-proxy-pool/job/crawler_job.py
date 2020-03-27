'''
Author: Yin, Evan Yalin
Date: 2019-8-27
Purpose: auto crawl free ip proxy
'''
import sys

sys.path.append('../')

import time
import traceback
from configparser import ConfigParser

from crawler import Crawler
from manager import ProxyManager
from utils import Util

log_file = 'crawler.log'
Util.log_to_file(
    'Crawler job is starting up at {0}.'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), 0,
    log_file)
while True:
    Util.log_to_file('Crawler job wake up and check if crawled proxy queue is idle.', 0, log_file)
    try:
        if ProxyManager.is_queue_idle():
            Util.log_to_file('Crawled proxy queue is idle, crawler begin crawling.', 0, log_file)
            c = Crawler()
            c.start_crawl()
            Util.log_to_file('Crawling finished.', 0, log_file)


        cp = ConfigParser()
        cp.read('config', encoding='utf-8')
        interval = cp.get('scheduler', 'crawler_interval')

        Util.log_to_file('Crawler job begin to sleep.', 0, log_file)
        time.sleep(int(interval) * 60)
    except:
        Util.log_to_file(traceback.format_exc(), 1, log_file)
        Util.log_to_file('Crawler job failed running, this job will be shutdown.', 0, log_file)

        break

Util.log_to_file(
    'Crawler job is ending at {0}.'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), 0,
    log_file)
