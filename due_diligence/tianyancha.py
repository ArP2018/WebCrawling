# encoding: utf-8
import time
from configparser import ConfigParser

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from geetest import GeetestCracker
from utils import get_driver

_author = 'Evan Yin'


class TianYanCha():
    def __init__(self):
        self.driver = get_driver()
        self.wait = WebDriverWait(self.driver, 15)
        self._cp = ConfigParser()
        self._cp.read('config')

    def login(self):
        '''
        登录天眼查
        :return:
        '''

        url = self._cp.get('Url', 'login_url')
        mobile = self._cp.get('Auth', 'mobile')
        password = self._cp.get('Auth', 'password')

        self.driver.get(url)
        self.wait.until(lambda _driver: _driver.find_element(By.CLASS_NAME, 'loginmodule').is_displayed())
        time.sleep(1)
        self.driver.find_element_by_xpath('//div[contains(text(), "密码登录")]').click()
        # self.driver.execute_script("return changeCurrent(1);")

        login_module = self.driver.find_element(By.CLASS_NAME, 'loginmodule')
        username_box = login_module.find_element(By.CLASS_NAME, 'contactphone')
        password_box = login_module.find_element(By.CLASS_NAME, 'input-pwd')
        login_btn = login_module.find_elements(By.XPATH, '//div[@class="btn -hg btn-primary -block"]')[2]

        username_box.send_keys(mobile)
        password_box.send_keys(password)
        login_btn.click()
        time.sleep(2)

        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gt_popup_wrap')))
            # _wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'search_button')))
        except TimeoutException:
            print(u'connection failed')
            return False
        except NoSuchElementException:
            print(u'login error, please check your login info')
            return False

        return True

    def crack_checkcode(self):
        '''
        模拟破解滑块验证码
        :return:
        '''
        cracker = GeetestCracker(self.driver)
        cracker.crack()
        time.sleep(1)

    def search_by_entity_name(self, name):
        '''
        根据公司名称获取搜索结果
        :param name:
        :return:
        '''
        url = self._cp.get('Url', 'search_url') + name
        self.driver.get(url)
        # print(self.driver.page_source)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        tags = soup.find_all('div', attrs={'class': 'search-item sv-search-company'})
        for t in tags:
            temp = t.find('div', attrs={'class': 'header'}).find('a')
            if temp.text == name:
                try:
                    self.driver.get(temp.attrs['href'])
                    time.sleep(1)
                    self.detail_soup = BeautifulSoup(self.driver.page_source, 'lxml')
                    return True
                except:
                    return False
        return False

    def parse_children_entity(self):
        '''
        获取子公司列表
        :return:
        '''
        self.detail_soup

    def parse_lawsuit(self):
        '''
        法律文书模块
        :return:
        '''
        self.driver.get()


if __name__ == '__main__':
    tyc = TianYanCha()
    tyc.login()
    tyc.crack_checkcode()
    url = tyc.search_by_entity_name('天津房地产集团有限公司')
    tyc.parse_children_entity()
