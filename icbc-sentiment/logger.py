# encoding: utf-8
# author: Yin Yalin
# purpose: 自定义日志类
import datetime
import logging
import os


class LogType(object):
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    WARNING = logging.WARNING
    ERROR = logging.ERROR


class CustomLogging(object):

    @classmethod
    def log_to_file(cls, log_str, log_type: LogType, log_file=''):
        if log_file == 'Null' or log_file == '':
            base_folder = 'Logs'
            if not os.path.exists('Logs'):
                os.mkdir(base_folder)
            log_file = "{0}\{1}.log".format(base_folder, datetime.datetime.now().strftime("%Y%m%d"))

            logging.basicConfig(level=LogType.INFO, filename=log_file, filemode='a',
                                format='%(asctime)s - %(levelname)s: %(message)s',)

            if log_type == LogType.DEBUG:
                logging.debug(log_str)
            elif log_type == LogType.INFO:
                logging.info(log_str)
            elif log_type == LogType.WARNING:
                logging.warning(log_str)
            else:
                logging.error(log_str)


if __name__ == '__main__':
    CustomLogging.log_to_file('hahsahhd', LogType.INFO, )
