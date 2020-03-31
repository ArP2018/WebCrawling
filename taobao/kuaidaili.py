import requests
from bs4 import BeautifulSoup

url = 'https://www.kuaidaili.com/ops/proxylist/'
header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
}

for i in range(1, 10):
    resp = requests.get(url, headers=header)
    soup = BeautifulSoup(resp.text, 'lxml')

    for tr in soup.find('div', id='freelist').find_all('tr')[1:]:
        tds = tr.find_all('td')
        ip, port, proxy_type = tds[0].text, tds[1].text, tds[3].text
        print(ip, port, proxy_type)
        if 'HTTPS' in proxy_type.upper():
            check_proxy(ip, port)