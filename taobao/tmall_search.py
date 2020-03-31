import random
import re
import time

import requests
from bs4 import BeautifulSoup

cookie = 'cna=npykFSY0/D8CAbfmoiZxuRf0; _m_h5_tk=af5d804215ac963819fb41378c81aa22_1562436398081; _m_h5_tk_enc=ea19d5409eec25e8fc7c259626899d7e; _med=dw:1536&dh:864&pw:1920&ph:1080&ist:0; _tb_token_=ebb3677979b7e; t=b1a580763cf37638852b9ef7282e0eb6; cookie2=19426288489c5da40f265fa6ff527c68; hng=CN%7Czh-cn%7CCNY; uc1=cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&cookie21=U%2BGCWk%2F7pY%2FF&cookie15=VT5L2FSpMGV7TQ%3D%3D&existShop=false&pas=0&cookie14=UoTaGqnHUwfYxw%3D%3D&tag=8&lng=zh_CN; ck1=""; unb=78222083; lgc=ynyalin; cookie1=Vvir4cZpSC%2F2MLdeOS7ZHdv32wj0RcehhpR8ch%2FcNwk%3D; login=true; cookie17=VAmolpsiHzg%3D; _l_g_=Ug%3D%3D; _nk_=ynyalin; tracknick=ynyalin; uss=""; csg=0bb87c40; skt=67e443932a1fed41; uc3=vt3=F8dBy3%2F4sjhLk6mMC44%3D&id2=VAmolpsiHzg%3D&nk2=GgWn4S2EIg%3D%3D&lg2=V32FPkk%2Fw0dUvg%3D%3D; enc=8NFurA%2Fy2GRZmU%2BAYS2JDzz5wyrG%2FvxeMyjFlgbu%2F%2FJYkyjZS0s0OUly380%2FTO8ywJgJe02XIXYkco2a%2BymNbA%3D%3D; _uab_collina=156243155825267261105943; x5sec=7b22746d616c6c7365617263683b32223a223337313162346239643437353564303064616431383763363566666561343230434d6167672b6b46454d6d477a62546f6e59484859426f4b4e7a67794d6a49774f444d374d513d3d227d; res=scroll%3A1263*5488-client%3A1263*611-offset%3A1263*5488-screen%3A1280*720; cq=ccp%3D0; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; swfstore=269243; x=__ll%3D-1%26_ato%3D0; pnm_cku822=098%23E1hv9vvUvbpvUvCkvvvvvjiPRFqpsji2nLsUgjivPmPOgji8PszZAjt8n2Myljt82QhvCvvvMMGEvpCWv3XnLBll5FpZDVQEfaAK5d8rJm765B4AdBQaUVllHd8re369D70Xd3w0EZKa6Lp7%2BulgEfFCKdy6Hmx%2Flj7ZHd8raoF6D40Od3Y%2FBIyCvvOCvhE2znoivpvUvvCC8kPpHp7tvpvIvvCvpvvvvvvvvhxHvvvC%2BpvvBZZvvvHIvvCHBpvvvxZvvhxHvvvCxphCvvOv9hCvvvvtvpvhvvCvp8wCvvpvvhHh; whl=-1%260%260%260; isg=BNHRB9gAaMCNToTpjcBVU4f54N3HLke3aneGWbNnxhj_WvOs-o-ygBr4_G4Z0t3o; l=bBaZSzDnqPRK9iG2BOfZZQKbU1_TmIOb8sPP2NJMwICP_K1Ry66lWZnvuiTvC3GVZ1RWJ38tRsQeBALFiyIV.'

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
    # 'cookie': cookie
}

data_path = './data/temp/'
url = 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.0.0.753b6208qcoEwU&s={0}&q=%CF%B4%B7%A2%CB%AE&sort=s&style=g&from=mallfp..pc_1_searchbutton&active=2&type=pc#J_Filte'

# import proxy_util as util
# proxies = util.Proxies("https")
# requestUtil = util.RequestUtility()

for i in range(22, 80):
    # resp = requestUtil.get(url.format(str(i*60-60)), headers=header, proxies=proxies)
    resp = requests.get(url.format(str(i * 60 - 60)), headers=header)
    soup = BeautifulSoup(resp.content, 'lxml')

    print('current page: {0}'.format(str(i)))
    current_path = data_path + 'page_{0}.csv'.format(str(i))
    with open(current_path, 'a', encoding='utf_8_sig') as f:
        f.write('data_id, sku_id, title' + '\n')

    product_list = soup.find_all('div', class_='product ')
    for p in product_list:
        product_id = p.attrs['data-id']
        title = p.find('p', class_='productTitle').find('a').attrs['title']
        url = p.find('p', class_='productTitle').find('a').attrs['href'].lstrip('//')
        sku_id = re.findall(re.compile('skuId=(\d*)&'), url)[0]
        shop = p.find('div', class_='productShop').find('a').text
        print(product_id, sku_id, title)

        with open(current_path, 'a', encoding='utf_8_sig') as f:
            f.write('{0}, {1}, {2} \n'.format(product_id, sku_id, title))

    time.sleep(2 + random.random())
