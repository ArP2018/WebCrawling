# encoding: utf-8
# author: Yin Yalin
# purpose: 通用方法文件

import configparser
import datetime
import math
import os
import re


def filter_url():
    # 过滤重复的url
    pass


def conv_pub_date(str_date, site):
    # 转换各种形式的日期字符串
    # cp = configparser.ConfigParser()
    if site == 'STCN' or site == 'cnstock':
        d = datetime.datetime.strptime(str_date.strip(), '%Y-%m-%d %H:%M')
    elif site in ('ifeng', 'yicai', 'peoplecn', 'hexun_news', 'sina'):
        d = datetime.datetime.strptime(str_date.strip(), '%Y-%m-%d %H:%M:%S')
    elif site in ('hexun'):
        d = datetime.datetime.strptime(str_date.strip(), '%b %d, %Y')
    elif site in ('hexun_blog'):
        d = datetime.datetime.strptime(str_date.strip(), '%Y年%m月%d日 %H:%M')
    elif site in ('cnfol', 'mrjj', 'sougou', 'bjsat'):
        d = datetime.datetime.strptime(str_date.strip(), '%Y-%m-%d')
    elif site in ('bjgsj'):
        d = datetime.datetime.strptime(str_date.strip(), '%Y.%m.%d %H:%M')
    elif site in ('baidu'):
        d = datetime.datetime.strptime(str_date.strip(), '%Y年%m月%d日')
    return d


def format_sougou_date(str_date):
    comp1 = re.compile('[1-9]\d{3}-(0?[1-9]|1[0-2])-(0?[1-9]|[1-2][0-9]|3[0-1])')
    comp2 = re.compile('[1-9]小时前')
    comp3 = re.compile('([1-9])天前')
    result1 = re.search(comp1, str_date)
    result2 = re.search(comp2, str_date)
    result3 = re.search(comp3, str_date)
    if result1:
        return result1.group()
    elif result2:
        str_d = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        return str_d
    elif result3:
        gap = int(result3.group()[0])
        d = datetime.datetime.now() + datetime.timedelta(days=-gap)
        str_d = datetime.datetime.strftime(d, '%Y-%m-%d')
        return str_d
    else:
        return ''


# 判断新闻日期是不是在指定日期内，一年内或两年内
def in_date_range(date, year):
    '''
    根据传入的日期判断该日期是不是在指定的年份内
    :param date: 需要判断的日期
    :param year: 指定年份
    :return: 判断结果, True or False
    '''
    gap_days = (datetime.datetime.now() - date).days
    if gap_days <= int(year) * 365:
        return True
    return False


def changeTime(allTime):
    day = 24 * 60 * 60
    hour = 60 * 60
    min = 60
    if allTime < 60:
        return "%d 秒" % math.ceil(allTime)
    elif allTime > day:
        days = divmod(allTime, day)
        return "%d 天, %s" % (int(days[0]), changeTime(days[1]))
    elif allTime > hour:
        hours = divmod(allTime, hour)
        return '%d 小时, %s' % (int(hours[0]), changeTime(hours[1]))
    else:
        mins = divmod(allTime, min)
        return "%d 分, %d 秒" % (int(mins[0]), math.ceil(mins[1]))


def get_filepath():
    cp = configparser.ConfigParser()
    base_path = os.path.dirname(os.path.abspath(__file__))

    cp.read(os.path.join(base_path, 'config'))
    user_file_path = cp.get('output_path', 'file_path').strip()
    if user_file_path == '.':
        return 'crawler.xlsx'
    else:
        file_path = os.path.dirname(user_file_path)
        file_name = os.path.basename(user_file_path)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        return user_file_path


if __name__ == '__main__':
    # print(conv_pub_date('2018-07-07 08:30', 'STCN'))
    format_sougou_date('中国经济网 - www.ce.cn/x...3天前 -  - 快照 ')
