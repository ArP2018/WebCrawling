'''
Author: Yin, Evan Yalin
Date: 2019-8-10
Purpose:
'''

import logging.handlers
import random

import requests
from requests import ConnectTimeout
from requests.exceptions import ProxyError, ReadTimeout, ConnectionError as CE

from settings import USER_AGENTS


class Util:
    @staticmethod
    def valid_proxy(ip, port, proxy_type=None):
        '''
        验证http代理
        :param ip: 代理ip字符串
        :param port: 代理ip端口
        :return: 验证结果, True or False
        '''
        header = {'user-agent': random.choice(USER_AGENTS)}
        if proxy_type.lower() == 'http':
            proxy = {'http': 'http://{0}:{1}'.format(ip, str(port))}
            url = 'http://www.baidu.com'
        elif proxy_type.lower() == 'https':
            proxy = {'https': 'https://{0}:{1}'.format(ip, str(port))}
            url = 'https://www.baidu.com'
        else:
            print('Proxy type parameter should be http or https.')
            return False

        try:
            resp = requests.get(url, headers=header, proxies=proxy, timeout=5, )
            if resp.status_code == 200:
                print('[Available Proxy] {0}://{1}:{2}'.format(proxy_type, ip, port))
                return True
            else:
                return False
        except (ConnectTimeout, ReadTimeout, CE):
            print('[Timeout Error] {0}://{1}:{2}'.format(proxy_type, ip, port))
            return False
        except ProxyError:
            print('[Unavailable Proxy] {0}://{1}:{2}'.format(proxy_type, ip, port))
            return False
        except:
            print('[Validation Failed] {0}://{1}:{2}'.format(proxy_type, ip, port))

    @staticmethod
    def img_to_text():
        pass

    @staticmethod
    def log_to_file(log_msg: str, log_type: int, log_file=None):
        '''
        写日志
        :param log_msg: 日志内容
        :param log_type: 日志类型 0 代表普通信息, 1 代表错误
        :param log_file: 日志文件名
        :return:
        '''
        if log_file is None:
            log_file = 'log'

        handler = logging.handlers.RotatingFileHandler(filename=log_file, maxBytes=1024 * 1000 * 10,
                                                       backupCount=5,
                                                       encoding='utf-8', mode='a')
        logging.basicConfig(handlers=[handler], level=logging.INFO,
                            format="%(levelname)s - %(filename)s - %(asctime)s:  %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S", )

        if log_type == 0:
            logging.info(log_msg)
        elif log_type == 1:
            logging.error(log_msg)
        else:
            logging.debug(log_msg)


if __name__ == '__main__':
    ip = '117.191.11.73'
    port = 80
    #
    Util.valid_proxy(ip, port, proxy_type='http')
    # Util.log_to_file('hello', 0, 'hello')
