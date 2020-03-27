# encoding: utf-8
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='log.txt',
                    filemode='a')

import re
import sys
import os
import time
from export_invoice import write_to_excel
from import_invoice import get_invoices
from invoice_verify import InvoiceVerify

start_time = time.time()



try:
    with open('config', 'r', encoding='utf-8') as f:
        config_info = f.read()
        try:
            input_path = re.search(re.compile('SOURCE_EXCEL_PATH *\=( *\S+)'), config_info).group(1).strip()
            print(input_path)
            output_path = re.search(re.compile('TARGET_EXCEL_PATH *\=( *\S+)'), config_info).group(1).strip()
            print(output_path)
        except AttributeError:
            # logging.error('配置信息填写有误！')
            print('配置信息有误')
            sys.exit(0)

except IOError:
    # logging.error('配置文件打开失败，请检查配置文件是否存在！')
    print('配置文件不存在')
    sys.exit(0)

# 获取发票基本信息列表
invoice_list = get_invoices(input_path)

# 验证并爬取列表里的发票
invfy = InvoiceVerify()
invfy.start_validate(invoice_list)

# 将发票写入自定义的模板
write_to_excel(output_path)

# 清除临时数据

if os.path.exists('finished_invoice_temp'):
    os.remove('finished_invoice_temp')

for j in os.listdir('temp'):
    if '.json' in j:
        os.remove('temp/%s' % j)

end_time = time.time()

print('time spent: %s s' % (end_time - start_time))
print('invoice_count: %s' % len(invoice_list))
print('captha accuracy: %s%s' % (round(invfy.normal_fp/invfy.shibie_count*100, 2), '%'))
