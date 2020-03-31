from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    '''
    获取webdriver对象
    :return:
    '''
    # options = Options()
    # options.add_argument('--headless')

    driver = webdriver.Chrome(executable_path='driver/chromedriver.exe')
    return driver
