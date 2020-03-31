import requests

url = 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.0.0.4af3605axoepS1&s={0}&q={1}&sort=s&style=g&from=mallfp..pc_1_searchbutton'
cookie = 'hng=CN%7Czh-CN%7CCNY%7C156; lid=ynyalin; enc=pTcAcoJIHZqUqkRp8My9oq8rXEaNe0gA%2BWRB2%2BGf9zODephh4HwCWuU7wEQljUk9dZru2TOfsBP5APBFHOhkkQ%3D%3D; cna=+IUwFK3IkWwCAXHMiHodbLYS; _med=dw:1536&dh:864&pw:1920&ph:1080&ist:0; cq=ccp%3D1; otherx=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; _uab_collina=156257051398726034238095; sm4=500100; _m_h5_tk=6f1bd31685096da260c9a95a421bf888_1562645189463; _m_h5_tk_enc=af81df8f9d13c1031b95636f2c77e0de; tk_trace=1; t=0950350d33e651353eda06012c78a0f6; uc3=vt3=F8dBy3%2F4t9X3XZzrQ3Y%3D&id2=VAmolpsiHzg%3D&nk2=GgWn4S2EIg%3D%3D&lg2=Vq8l%2BKCLz3%2F65A%3D%3D; tracknick=ynyalin; lgc=ynyalin; _tb_token_=e3565e136183d; cookie2=13fb3cc08261e88bd25f343c33f24c70; swfstore=246489; res=scroll%3A990*6575-client%3A754*742-offset%3A754*6575-screen%3A1536*864; pnm_cku822=098%23E1hvVQvUvbpvjQCkvvvvvjiPRFqwsjE2n2qv6j3mPmPZgjYER2dUsjrbRFFUAjgtvpvhvvvvvvGCvvpvvPMMmphvLC2k%2Fvvjnr3l%2FPkAdcHVafmxfBeOjomxfwLOd3tGV7zhtjZ7%2B3%2Bu0jc6D40OJm7%2BD7zUe8t%2Bm7zhgj7JVcxveExr1CKKfvDrAWBl5F%2FtvpvIvvvvvhCvvvvvvUVCphvUzQvvvQCvpvACvvv2vhCv2RvvvvWvphvWg8yCvv9vvUmle3yewgyCvvOUvvVvaygCvpvVvvpvvhCviQhvCvvv9UU%3D; l=cBNLedjHqxXk8Wl3BOfwCuI8ah7OaIRb8sPzw4_GkICPOp59pLzCWZn5cdYpCnGVLsZWR3SIBC3vBoL3Yy4EhjxwFEkztuiA.; isg=BKmpgz3o0P3zTOxOtelfJv7quFXD3p3b199mI0ue-BCIEsgkk8eyeZ9A1PaBijXg'

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36',
    'cookie': cookie
}


def search(page_num, keyword):
    keyword = requests.utils.quote(keyword)
    resp = requests.get(url.format(page_num, keyword))

    print(resp.text)
    pass


search(60, '四件套')
