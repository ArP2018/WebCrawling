'''
Author: Yin, Evan Yalin
Date: 2019-8-27
Purpose: validate ip proxy queue
'''
import sys

sys.path.append('../')

import time
import traceback

from manager import ProxyManager
from utils import Util

#  refresh available ip proxy pool


log_file = 'validation.log'
Util.log_to_file(
    'Validation job is starting up at {0}.'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), 0,
    log_file)
while True:
    try:
        Util.log_to_file('Begin validating ip proxy queue.', 0, log_file)
        result = ProxyManager.validate()
    except:
        Util.log_to_file(traceback.format_exc(), 1, log_file)
        Util.log_to_file('Validation job failed running, this job will be shutdown.', 0, log_file)

        break

    Util.log_to_file('Validation job complete.', 0, log_file)
    time.sleep(600)

Util.log_to_file(
    'Validation job is ending at {0}.'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))), 0,
    log_file)
