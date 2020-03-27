# 门店评论
import re
import time
import traceback

import requests
from bs4 import BeautifulSoup

# 请求头信息设置
cookie = '_lxsdk_cuid=16c64f7207dc8-02862f23ee00e5-675c772b-144000-16c64f7207dc8; _lxsdk=16c64f7207dc8-02862f23ee00e5-675c772b-144000-16c64f7207dc8; _hc.v=6d24acc7-f7fd-ff00-e655-2d620b43464e.1565062014; dper=e06ceb550ed340a557835cc851ef8a7406b3c7db03555bfea79a0be318b863d0955e013c9ffce71c44c89bb399cbefe5ed41d9a2ce4f8e6da78bbfdba74cebcc4ece67f527e5fd7879fe6e0d4e66406de68de80b9fe64136a0e7aa17ca1759b2; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_7217891468; ctu=fce32f7237aec16b4bc9aa4582b5327c1502412ff8cfc0e583b4bf0da9d1bcfd; uamo=18996099502; _lxsdk_s=16c64f7207e-8a4-716-57e%7C%7C82'
header = {
    'cookie': cookie,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
}


def css_content(html_text):
    '''
    extract css url from html source code
    :param html_text:
    :return:
    '''
    css_url = 'http:' + re.findall(re.compile('href="(//s3plus\.meituan\.net.*?svgtextcss.*?\.css)"'), html_text)[0]
    print('css_url: ' + css_url)
    css_cont = requests.get(css_url, headers=header)
    return css_cont.text


def svg_parser(url):
    '''
    parse svg document content
    :param url:
    :return: svg content, font-size
    '''
    resp = requests.get(url, headers=header)
    # svg文件有两种格式，第一种使用text标签放文字内容（相当于是字典），第二种使用textPath标签放文字内容
    words_dic = re.findall(re.compile('y="(\d+)">(\w+)</text>'), resp.text)

    if not words_dic:
        words_dic = []
        words = re.findall(re.compile('textLength.*?(\w+)</textPath>'), resp.text)
        y = re.findall(re.compile('id="\d+" d="\w+\s(\d+)\s\w+"'), resp.text)
        for a, b in zip(y, words):
            words_dic.append((a, b))
    words_dic = [(int(i[0]), i[1]) for i in words_dic]
    font_size = re.findall(re.compile('font-size:(\d+)px'), resp.text)[0]

    return words_dic, font_size


def css_to_word(css_tag):
    '''
    根据class name和background坐标对匹配对应的文字
    :param css_tag: class name 以及background坐标对
    :return: 匹配到的文字
    '''
    css_class_name = css_tag[0]
    css_bg_x = css_tag[1]
    css_bg_y = css_tag[2]
    for words_dic in s_parser:
        code, words, size = words_dic['code'], words_dic['words'], words_dic['size']
        if code in css_class_name:
            # 如果|background[y]|值小于svg字典列表里第一行的y值时，需要匹配的文本就在第一行
            if int(css_bg_y) < int(words[0][0]):
                col_index = int(css_bg_x) // int(size)
                return words[0][1][col_index]
            # 如果|background[y]|值大于svg页面第n行的y值并且小于第n+1行的y值，则需要匹配的文本在第n+1行
            for idx, dic in enumerate(words[:-1]):
                dic_y, word_str = dic
                if int(css_bg_y) >= int(dic_y) and int(css_bg_y) < int(words[idx + 1][0]):
                    col_index = int(css_bg_x) // int(size)
                    return words[idx + 1][1][col_index]


def crawl_comments(shop_id):
    review_all_url = 'http://www.dianping.com/shop/{0}/review_all/p{1}'  # 97141784

    for i in range(1, 2):
        resp = requests.get(review_all_url.format(shop_id, str(i)), headers=header)

        css_cont = css_content(resp.text)

        svg_url = re.findall(re.compile('class\^="(\w+)".*?(//s3plus.*?\.svg)'), css_cont)
        global s_parser
        s_parser = []
        # class name以c开头的标签内的文字从对应的svg文件中进行匹配
        for c, u in svg_url:
            w, s = svg_parser('http:' + u)
            s_parser.append({'code': c, 'words': w, 'size': s})

        # 被css加密过的文字list
        css_list = re.findall(re.compile('\.(\w+){background:.*?(\d+).*?px.*?(\d+).*?px;}'), css_cont)

        decoded_list = []
        for c in css_list:
            word = css_to_word(c)
            decoded_list.append({'code': c[0], 'word': word})

        replaced_html_code = resp.text
        for d in decoded_list:
            if d['code'] in replaced_html_code:
                try:
                    replaced_html_code = re.sub(re.compile(f'<\w+\sclass="{d["code"]}"></\w+>'), d['word'],
                                                replaced_html_code)
                except:
                    print('匹配文本出错')
                    pass

        soup = BeautifulSoup(replaced_html_code, 'lxml')
        reviews = soup.find_all('div', class_='main-review')
        for r in reviews:
            user_name = r.find('div', class_='dper-info').find('a').text.strip()
            score = r.find('span', class_='score').text.replace('\n', '').strip()
            desc_hide = r.find('div', class_='review-words Hide')
            if desc_hide:
                desc = desc_hide.text.strip().replace('收起评论', '').strip()
            else:
                desc = r.find('div', class_='review-words').text.strip()

            print('user_name: ' + user_name)
            print('score: ' + score)
            print(desc)
            print('-' * 150)

            time.sleep(2)

        time.sleep(5)


#
def crawl_shop_list(keyword):
    search_url = 'https://www.dianping.com/search/keyword/2/0_{0}'.format(keyword)  # 2是城市id,此处代表北京
    resp = requests.get(search_url, headers=header)
    soup = BeautifulSoup(resp.text, 'lxml')
    urls = soup.find('div', id='shop-all-list').find_all('a', attrs={'data-click-name': 'shop_title_click'})
    for u in urls:
        shop_name = u.text
        shop_url = u.attrs['href']
        shop_id = shop_url.split('/')[-1]
        print(shop_id, shop_name, shop_url)


if __name__ == '__main__':
    with open('shop_list.csv', ) as f:
        ids = f.readlines()

    for id in ids:
        try:
            crawl_comments(id.strip('\n').strip())
        except:
            print(traceback.format_exc())
