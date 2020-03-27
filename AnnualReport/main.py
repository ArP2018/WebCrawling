import argparse

import time

import sys

from reportcrawler import GeneralCrawler

ap = argparse.ArgumentParser()
ap.add_argument('stockcode')
ap.add_argument('website', choices=['sse', 'szse'], help='sse is for shangjiaosuo, szse is for shenjiaosuo')
ap.add_argument('-k', '--keyword', help='to filter search results')
ap.add_argument('-s', '--starttime', help='to search report after this time')
ap.add_argument('-e', '--endtime', help='to search report before this time')

args = ap.parse_args()

stockcode, website = args.stockcode, args.website

if args.keyword:
    keyword = args.keyword
else:
    keyword = None

if args.starttime:
    try:
        f_date = time.strptime(args.starttime, '%Y%m%d')
        start_time = str(f_date.tm_year) + '-' + ('0' + str(f_date.tm_mon))[:2] + '-' + ('0' + str(f_date.tm_mday))[:2]
    except:
        print('开始时间参数格式错误，请使用格式"yyyymmdd" e.g.20180101')
        sys.exit()
else:
    start_time = None

if args.endtime:
    try:
        f_date = time.strptime(args.endtime, '%Y%m%d')
        end_time = str(f_date.tm_year) + '-' + ('0' + str(f_date.tm_mon))[:2] + '-' + ('0' + str(f_date.tm_mday))[:2]
    except:
        print('结束时间参数格式错误，请使用格式"yyyymmdd" e.g.20180101')
        sys.exit()
else:
    end_time = None

if args.starttime and args.endtime:
    # 结束日期必须大于开始日期
    if args.starttime > args.endtime:
        print('时间参数错误，结束时间必须大于开始时间')
        sys.exit()

        # 判断起始日期,上交所搜索范围不能大于三年
    if website == 'sse':
        a = time.strptime(start_time, '%Y-%m-%d')
        b = time.strptime(end_time, '%Y-%m-%d')
        if (b.tm_year - a.tm_year) * 12 + (b.tm_mon - a.tm_mon) > 36:
            print('上交所只提供日期间隔不超过3年的公告查询！')
            sys.exit()

if website == 'sse' and (args.starttime or args.endtime):
    print('上交所按时间搜索功能需要同时指定开始日期和结束日期或不指定（默认搜索最近三个月）')
    sys.exit()

s = time.time()

crawler = GeneralCrawler(website)
crawler.download_pdf(stockcode, s_date=start_time, e_date=end_time, keyword=keyword)
e = time.time()
print('爬取用时: %ss' % str(int(e - s)))
