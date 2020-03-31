# Import packages
import sys  # Python System Package
import requests  # HTTP Handler
from urllib.parse import quote  # URL Encode
from bs4 import BeautifulSoup  # HTML/XML Parser
import json  # JSON Parser
import time  # System Time Utility
from datetime import datetime  # Datetime Utility
import random  # Random Utilities
import csv  # CSV Reader


# Class ProxiesPool
class Proxies:
    proxy_list = []
    protocol = "https"

    # Instantiate Proxy Pool
    def __init__(self, proto):
        self.protocol = str(proto)
        self.refreshPool()

    # Randomly return a proxy from list
    def getProxy(self):
        proxyDict = {
            self.protocol: random.choice(self.proxy_list)
        }
        return proxyDict

    # Return proxies count
    def getCount(self):
        return len(self.proxy_list)

    # Remove entry from proxy list
    def remove(self, url):
        self.proxy_list.remove(url)
        # Refresh Proxy Pool when empty
        if len(self.proxy_list) <= 0:
            self.refreshPool()

    # Refresh Proxies Pool
    def refreshPool(self):
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
        }

        # 快代理
        url = "https://www.kuaidaili.com/ops/proxylist/"
        while (True):
            try:
                # Free Proxies link
                for i in range(1, 11):
                    print("Refilling proxies from url %s" % (url + str(i)))
                    resp = requests.get(url + str(i), headers=header)
                    soup = BeautifulSoup(resp.text, 'lxml')

                    proxy_rows = soup.find('div', id='freelist').find_all('tr')[1:]
                    for tr in proxy_rows:
                        tds = tr.find_all('td')
                        ip, port, proxy_type = tds[0].text, tds[1].text, tds[3].text
                        if 'HTTPS' in proxy_type.upper():
                            self.proxy_list.append('https://{0}:{1}'.format(ip, port))

                # Exit loop when succeeded
                break

            except:
                print("Error connecting to url %s" % url)
                print("Retrying in 3 seconds ... ")

                # Flush stdout and Wait for some time
                sys.stdout.flush()
                time.sleep(1)

                continue

        # # 西祠代理
        # url = 'https://www.xicidaili.com/nn/'
        # while (True):
        #     try:
        #         for i in range(1, 4):
        #             print("Refilling proxies from url %s" % (url + str(i)))
        #             resp = requests.get(url + str(i), headers=header)
        #             soup = BeautifulSoup(resp.text, 'lxml')
        #
        #             proxy_rows = soup.find('table', id='ip_list').find_all('tr')[1:]
        #             for tr in proxy_rows:
        #                 tds = tr.find_all('td')
        #                 ip, port, proxy_type = tds[1].text, tds[2].text, tds[5].text
        #                 if 'HTTPS' in proxy_type.upper():
        #                     self.proxy_list.append('https://{0}:{1}'.format(ip, port))
        #
        #         # Exit loop when succeeded
        #         break
        #
        #     except:
        #         print("Error connecting to url %s" % url)
        #         print("Retrying in 3 seconds ... ")
        #
        #         # Flush stdout and Wait for some time
        #         sys.stdout.flush()
        #         time.sleep(1)
        #
        #         continue
        # End while
    # End def


# End Class ProxiesPool

# Class Headers
class Headers:
    headers = {}

    # Custom User Agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3)",
        "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16C101 MicroMessenger/7.0.3(0x17000321) NetType/4G Language/zh_CN",
        'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    ]

    # Instantiate Object
    def __init__(self):
        self.headers = {
            "User-Agent": random.choice(self.user_agents)
        }

    # Get Headers Info
    def getHeaders(self):
        return self.headers

    # Update Header
    def updateHeaders(self, key, value):
        self.headers[key] = value


# End class HeadersPool

# Class RequestUtility
class RequestUtility:

    # Instantiate object
    def __init__(self):
        pass

    def get_with_retry_limit(self, url, headers, proxies, retries):
        for trial in range(retries):
            proxy = proxies.getProxy()
            try:
                print("Using HTTPS Proxy: %s" % proxy["https"])
                sys.stdout.flush()
                response = requests.get(url=url, headers=headers, proxies=proxy, timeout=5)
                return response
            except TimeoutError:
                proxies.remove(proxy["https"])
                print("Timeout Error. Retrying request ...")
                continue
            except:
                proxies.remove(proxy["https"])
                print("Unexpected Error. Retrying request ...")
                continue
            # End try
        print("Max retry %d reached." % retries)
        # End for

    # End def

    def get(self, url, headers, proxies):
        while (True):
            proxy = proxies.getProxy()
            try:
                print("Using https proxy: %s" % proxy["https"])
                response = requests.get(url=url, headers=headers, proxies=proxy, timeout=3)
                return response
            except:
                proxies.remove(proxy["https"])
                print("Error connecting to proxy. Retrying with another https proxy ...")
                continue
            # End try
        # End while loopS
    # End def
# End Class RequestUtility
