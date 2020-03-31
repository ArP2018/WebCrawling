from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(executable_path='driver/chromedriver.exe', options=options)
driver.set_window_size(1024, 960)

url_list = [
# 'https://www.qichacha.com/wenshuDetail_com_c2502bb205ab9c95b29d29f701290ebe.html',
# 'https://www.qichacha.com/wenshuDetail_com_fba6d4dbf5ca4884151dbefea60429d2.html',
# 'https://www.qichacha.com/wenshuDetail_com_9736652aded1ce1a7432491681817dad.html',
# 'https://www.qichacha.com/wenshuDetail_com_b66b87e0c5212f5d01a0c2f92b89b57c.html',
# 'https://www.qichacha.com/wenshuDetail_com_ae1012a7c1225f7c4071dc512bd265b6.html',
# 'https://www.qichacha.com/wenshuDetail_com_101d706f81e23eeedcdc92e9c4bb6885.html',
# 'https://www.qichacha.com/wenshuDetail_com_17f107188f6e10fbf5daa84cd6e1391a.html',
# 'https://www.qichacha.com/wenshuDetail_com_1afd1c0d56b943e04de76b52ab2e6ae4.html',
# 'https://www.qichacha.com/wenshuDetail_com_1212e7a0d1a67a9f781ea454b6995488.html',
# 'https://www.qichacha.com/wenshuDetail_com_20b4810726cc104f0277650b605b28bc.html'
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/decided_punishment/201501/t20150105_13234.html',
    'http://xzzf.hbzwfw.gov.cn/punish/getPunishById?id=2625666',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/decided_punishment/201710/t20171023_29992.html',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/decided_punishment/201705/t20170524_27335.html',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/decided_punishment/201701/t20170104_25174.html',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/environmentalviolations_timelimit_decision/201512/t20151210_18735.html',
    'http://xzzf.hbzwfw.gov.cn/punish/getPunishById?id=2625666',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/decided_punishment/201708/t20170825_29152.html',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/environmentalviolations_timelimit_decision/201708/t20170825_29152.html',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/environmentalviolations_timelimit_decision/201410/t20141024_2266.html',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/environmentalviolations_timelimit_decision/201410/t20141024_2247.html',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/environmentalviolations_timelimit_decision/201410/t20141021_1931.html',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/decided_punishment/201703/t20170327_26284.html',
    'http://hjbh.tj.gov.cn/env/supervised_pollution_info/administrative_penalty/decided_punishment/201507/t20150702_16113.html',
    'http://xzzf.hbzwfw.gov.cn/punish/getPunishById?id=2631811',
    'http://xzzf.hbzwfw.gov.cn/punish/getPunishById?id=2631810',
    'http://xzzf.hbzwfw.gov.cn/punish/getPunishById?id=2631827',
    'http://xzzf.hbzwfw.gov.cn/punish/getPunishById?id=2631788',
    'http://xzzf.hbzwfw.gov.cn/punish/getPunishById?id=2622217',
    'http://www.cbrc.gov.cn/chinese/home/docView/DEDC9952DD914C47A7020DF78314DC7F.html',
    'http://www.cbrc.gov.cn/chinese/home/docView/BFB57321D0F244AD8F3988B1F03A8D8D.html',
    'http://www.cbrc.gov.cn/chinese/home/docView/AFA2B02A8BE34EEA882F260A06AF7451.html',
    'http://www.cbrc.gov.cn/chinese/home/docView/6B7955D294874C86900669FF062DD5A9.html',

]
for i, url in enumerate(url_list):
    n = i + 5732
    driver.get(url)
    driver.maximize_window()
    driver.save_screenshot('snapshots/{0}.png'.format(str(n)))

driver.quit()
