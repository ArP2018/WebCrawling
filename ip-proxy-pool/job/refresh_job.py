'''
Author: Yin, Evan Yalin
Date: 2019-8-27
Purpose: refresh ip proxy pool
'''
import sys

sys.path.append('../')

import time
import traceback
from configparser import ConfigParser

from manager import ProxyManager
from utils import Util

#  refresh available ip proxy pool


log_file = 'refresh.log'
Util.log_to_file(
    'Refresh job is starting up at {0}.'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), 0,
    log_file)
while True:
    try:

        Util.log_to_file('Start refreshing proxy pool.', 0, log_file)
        result = ProxyManager.refresh_proxy_pool()
        Util.log_to_file('Refresh finished.', 0, log_file)
        Util.log_to_file(result, 0, log_file)

        cp = ConfigParser()
        cp.read('config', encoding='utf-8')
        interval = cp.get('scheduler', 'refresh_interval')

        Util.log_to_file('Refresh job begin to sleep.', 0, log_file)
        time.sleep(int(interval) * 60)

        Util.log_to_file('Refresh job wake up and start next refresh.', 0, log_file)
    except:
        Util.log_to_file(traceback.format_exc(), 1, log_file)
        Util.log_to_file('Refresh job failed running, this job will be shutdown.', 0, log_file)

        break

Util.log_to_file(
    'Refresh job is ending at {0}.'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), 0,
    log_file)
