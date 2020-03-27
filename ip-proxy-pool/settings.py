REDIS_HOST = '10.13.38.15'
REDIS_PORT = 6379
REDIS_PASSWORD = 'Dttdai123'

# config request header
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36']

CRAWLED_SITES = {
    # '0': 'xicidaili',
    # '1': 'kuaidaili',
    # '2': 'jisudaili',
    # '3': 'wuyoudaili',
    # '4': 'yundaili',
    # '5': 'xiaoshudaili',
    # '6': 'zhandaye',
    # '7': 'mipudaili',   # ocr图片转文本还未实现,
    # '8': 'xiladaili',
    # '9': 'nimadaili',
    '10': 'wannengdaili'
}

PHANTOMJS_PATH = './driver/phantomjs.exe'
CHROME_DRIVER_PATH = './driver/chromedriver.exe'

# 存放验证成功的代理
VALIDATED_HTTP_KEY = 'proxy:validated:http_set'
VALIDATED_HTTPS_KEY = 'proxy:validated:https_set'
# 存放已爬取的代理
CRAWLED_POOL_KEY = 'proxy:crawled:list'
