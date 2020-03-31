# author: Yin Yalin
# purpose: 程序入口文件
import argparse
import os
import sys
import time
import traceback

from CE import CE_Sougou
from CNStock import CNStock
from EastMoney import EastMoneyFinance, EastMoneyTieba, EastMoneyBlog
from HeXun import HeXun
from IFengFinance import IFengFinance
from PeopleCN import PeopleCN
from STCN import STCN
from SinaFin import SinaFin
from SouhuFin import SouhuFin
from TencentFin import TencentFin
from YiCai import YiCai
from bjgsj import BJGSJ
from bjsat import BJSAT
from cnfol import CNFOL
from logger import CustomLogging, LogType
from mrjj import  Mrjj_Sougou
from qianlong import QianLong
from configparser import ConfigParser

from thsh import TongHuaShun
from tianyancha import TianYanCha
from utils import changeTime, get_filepath

ap = argparse.ArgumentParser()
ap.add_argument('keywords_arg')
ap.add_argument('-y', '--year', help='crawl how many years data')

keywords_arg = sys.argv[1]
keywords = keywords_arg.split(',')

try:
    save_file_path = get_filepath()
except:
    CustomLogging.log_to_file(traceback.format_exc(), LogType.ERROR)
    print('配置文件路径出错，程序即将退出')
    sys.exit(0)

args = ap.parse_args()
if args.year:
    year = args.year
else:
    year = 1
print('爬取关键字: {0}。  爬取年限: {1}年内'.format(keywords_arg, year))

cp = ConfigParser()
file_path = os.path.dirname(os.path.abspath(__file__))
cp.read(os.path.join(file_path, 'config'))
cp.read('config')
sites = cp.options('websites')

start_time = time.time()
success_count = 0

for site_name in sites:
    try:
        crawling_site = ''
        if site_name == 'stcn':
            # 证券时报
            stcn = STCN()
            crawling_site = stcn.name
            print('准备检索网站: %s ' % stcn.name)
            stcn.start_crawl(keywords, year_range=year)
            stcn.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'cnstock':
            # 中国证券网
            cnstock = CNStock()
            crawling_site = cnstock.name
            print('准备检索网站:%s ' % cnstock.name)
            cnstock.start_crawl(keywords, year_range=year)
            cnstock.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'ifeng':
            # 凤凰财经
            ifeng = IFengFinance()
            crawling_site = ifeng.name
            print('准备检索网站:%s ' % ifeng.name)
            ifeng.start_crawl(keywords, year_range=year)
            ifeng.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'yicai':
            # 第一财经
            yicai = YiCai()
            crawling_site = yicai.name
            print('准备检索网站:%s ' % yicai.name)
            yicai.start_crawl(keywords, year_range=year)
            yicai.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'pc':
            # 人民网
            pc = PeopleCN()
            crawling_site = pc.name
            print('准备检索网站:%s ' % pc.name)
            pc.start_crawl(keywords, year_range=year)
            pc.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'ce':
            # 中国经济网
            ce = CE_Sougou('ce.cn')
            crawling_site = ce.name
            print('准备检索网站:%s ' % ce.name)
            ce.start_crawl(keywords, year_range=year)
            ce.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'ql':
            # 千龙网
            ql = QianLong('qianlong.com')
            crawling_site = ql.name
            print('准备检索网站:%s ' % ql.name)
            ql.start_crawl(keywords, year_range=year)
            ql.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'hexun':
            hexun = HeXun()
            crawling_site = hexun.name
            print('准备检索网站:%s ' % hexun.name)
            hexun.start_crawl(keywords)
            hexun.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'sina':
            # 新浪财经
            sina = SinaFin()
            crawling_site = sina.name
            print('准备检索网站:%s ' % sina.name)
            sina.start_crawl(keywords, year_range=year)
            sina.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'cnfol':
            # 中金在线
            cnfol = CNFOL()
            crawling_site = cnfol.name
            print('准备检索网站:%s ' % cnfol.name)
            cnfol.start_crawl(keywords, year_range=year)
            cnfol.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'mrjj':
            mrjj = Mrjj_Sougou('nbd.com.cn')
            crawling_site = mrjj.name
            print('准备检索网站:%s ' % mrjj.name)
            mrjj.start_crawl(keywords)
            mrjj.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'tencent':
            # 腾讯财经
            tencent = TencentFin('news.qq.com')
            crawling_site = tencent.name
            print('准备检索网站:%s ' % tencent.name)
            tencent.start_crawl(keywords, year_range=year)
            tencent.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'souhu':
            # 搜狐财经
            souhu = SouhuFin('business.sohu.com')
            crawling_site = souhu.name
            print('准备检索网站:%s ' % souhu.name)
            souhu.start_crawl(keywords, year_range=year)
            souhu.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'eastmoney':
            # 东方财富网
            emf = EastMoneyFinance('finance.eastmoney.com')
            crawling_site = emf.name
            print('准备检索网站:%s ' % emf.name)
            emf.start_crawl(keywords, year_range=year)
            emf.write_to_excel(save_file_path)

            emt = EastMoneyTieba('guba.eastmoney.com')
            crawling_site = emt.name
            print('准备检索网站:%s ' % emt.name)
            emt.start_crawl(keywords, year_range=year)
            emt.write_to_excel(save_file_path)

            emb = EastMoneyBlog('blog.eastmoney.com')
            crawling_site = emb.name
            print('准备检索网站:%s ' % emb.name)
            emb.start_crawl(keywords, year_range=year)
            emb.write_to_excel(save_file_path)

            success_count += 1
        elif site_name == 'bjgsj':
            # 北京工商局
            gsj = BJGSJ()
            crawling_site = gsj.name
            print('准备检索网站:%s ' % gsj.name)
            gsj.start_crawl(keywords, year_range=year)
            gsj.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'bjsat':
            # 北京税务局
            bjsat = BJSAT()
            crawling_site = bjsat.name
            print('准备检索网站:%s ' % bjsat.name)
            bjsat.start_crawl(keywords, year_range=year)
            bjsat.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'thsh':
            # 同花顺
            thsh = TongHuaShun('10jqka.com.cn')
            crawling_site = thsh.name
            print('准备检索网站:%s ' % thsh.name)
            thsh.start_crawl(keywords, year_range=year)
            thsh.write_to_excel(save_file_path)
            success_count += 1
        elif site_name == 'tianyancha':
            # 天眼查
            tyc = TianYanCha()
            crawling_site = tyc.name
            print('准备检索网站:%s ' % tyc.name)
            tyc.start_crawl(keywords, )
            tyc.write_to_excel(save_file_path)
            success_count += 1
        else:
            pass
    except:
        print('{0} 爬取出错,即将开始爬取下一网站......'.format(crawling_site))
        CustomLogging.log_to_file(traceback.format_exc(), LogType.INFO)

end_time = time.time()

print('爬取完毕, 结果保存至{0} \n'
      '成功检索网站 {1} 个, 耗时 {2}'.format(os.path.join(os.path.abspath(os.path.curdir), 'crawler.xlsx'), success_count,
                                    changeTime(end_time - start_time)))
