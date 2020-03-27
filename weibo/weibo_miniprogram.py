import random
import sys
import time
import traceback
from sys import argv

import pymysql
import requests

from settings import DB_HOST, DB_INSTANCE, DB_USERNAME, DB_PASSWORD

# for dior
url = 'https://api.weibo.cn/2/cardlist?containerid=231051_-_fans_-_2130860695&gsid=_2A_p8jQA0CoV0kysgkAzRTFoM2M3lPcwrBy7-zmFeEtLG4IFeQ4FQWFSEbx4WyCw1f6hqC2nH_l3XdR2qYLeGJZmF&c=weixinminiprogram&s=acda457e&wm=90163_90001&from=1885396040&uid=6300868139&since_id={0}&count=20'
#
# blog_url = 'https://api.weibo.cn/2/profile/statuses?containerid=1076032130860695&gsid=_2A_p8jQA0CoV0kysgkAzRTFoM2M3lPcwrBy7-zmFeEtLG4IFeQ4FQWFSEbx4WyCw1f6hqC2nH_l3XdR2qYLeGJZmF&from=1885396040&wm=90163_90001&c=weixinminiprogram&s=acda457e&lang=zh_CN&page={0}'
# comment_url = 'https://api.weibo.cn/2/comments/build_comments?new_version=0&max_id={max_id}&is_show_bulletin=2&c=weixinminiprogram&s=acda457e&id={blog_id}&wm=90163_90001&v_f=2&v_p=60&from=1885396040&gsid=_2A_p8jQA0CoV0kysgkAzRTFoM2M3lPcwrBy7-zmFeEtLG4IFeQ4FQWFSEbx4WyCw1f6hqC2nH_l3XdR2qYLeGJZmF&uid=6300868139&count=20&isGetLongText=1&fetch_level=0&max_id_type=0'

blog_url = 'https://api.weibo.cn/2/profile/statuses?containerid=1076031924007153&gsid=_2A_p8jQA0CoV0kysgkAzRTFoM2M3lPcwrBy7-zmFeEtLG4IFeQ4FQWFSEbx4WyCw1f6hqC2nH_l3XdR2qYLeGJZmF&from=1885396040&wm=90163_90001&c=weixinminiprogram&s=acda457e&lang=zh_CN&page={0}'
comment_url = 'https://api.weibo.cn/2/comments/build_comments?new_version=0&max_id={max_id}&is_show_bulletin=2&c=weixinminiprogram&s=acda457e&id={blog_id}&wm=90163_90001&v_f=2&v_p=60&from=1885396040&gsid=_2A_p8jQA0CoV0kysgkAzRTFoM2M3lPcwrBy7-zmFeEtLG4IFeQ4FQWFSEbx4WyCw1f6hqC2nH_l3XdR2qYLeGJZmF&uid=6300868139&count=20&isGetLongText=1&fetch_level=0&max_id_type=0'

db_conn = pymysql.connect(host=DB_HOST, user=DB_USERNAME, password=DB_PASSWORD, database=DB_INSTANCE, )
db_cursor = db_conn.cursor()


class WeiboUser:
    u_id = ''
    u_name = ''
    u_screen_name = ''
    u_signature = ''
    u_follower_count = ''


class WeiboArticle:
    article_id = ''
    create_date = ''
    content = ''
    comment_count = ''
    forward_count = ''  # reports_count
    like_count = ''  # attitudes_count


class WeiboComment:
    article_id = ''
    created_date = ''
    content = ''
    like_count = ''
    comment_user_id = ''


def crawl(page):
    resp = requests.get(url.format(page), headers={'x-sessionid': 'd7fa41deef3054b6bf06f3c7349bd941'})
    return resp.json()


def save_weibo_user(w: WeiboUser):
    sql = 'insert into weibo_user(user_id, screen_name,name,signature, followers_count) values(%s, %s, %s, %s, %s)'
    try:
        db_cursor.execute(sql, (w.u_id, w.u_screen_name, w.u_name, w.u_signature, w.u_follower_count))
        db_conn.commit()
    except:
        print(traceback.format_exc())


def start_crawl():
    for i in range(2, 5000):
        try:
            print('current page: %s' % str(i))
            result = crawl(str(i))
        except:
            print(traceback.format_exc())
            break

        try:
            followers = result.get('cards')[0].get('card_group')
        except:
            print(traceback.format_exc())
            break

        try:
            for f in followers:
                user = WeiboUser()
                user.u_id = f.get('user').get('id')
                user.u_screen_name = f.get('user').get('screen_name')
                user.u_name = f.get('user').get('name')
                user.u_signature = f.get('desc1')
                user.u_follower_count = f.get('user').get('followers_count')

                print(user.u_id, user.u_screen_name, user.u_name, user.u_signature, user.u_follower_count)

                save_weibo_user(user)

        except:
            print(traceback.format_exc())

        time.sleep(5 + random.random())


def save_weibo_article(a: WeiboArticle):
    sql = 'insert into weibo_article(article_id, content,create_date,comment_count, forward_count, like_count) values(%s, %s, %s, %s, %s, %s)'
    try:
        db_cursor.execute(sql, (a.article_id, a.content, a.create_date, a.comment_count, a.forward_count, a.like_count))
        db_conn.commit()
    except:
        print('insert weibo article failure')
        print(traceback.format_exc())


def crawl_blog(page):
    resp = requests.get(blog_url.format(page), headers={'x-sessionid': 'adc9a6c52f1dbd211bbef9867249b33c'})

    if resp.status_code != 200:
        time.sleep(10)
        crawl_blog(page)
    return resp.json()


def crawl_blog_comment(max_id, blog_id):
    print(comment_url.format(max_id=max_id, blog_id=blog_id))
    try:
        resp = requests.get(comment_url.format(max_id=max_id, blog_id=blog_id),
                            headers={'x-sessionid': 'a74fd524bcf8ebf0f88c90268bc04da1'})

        if resp.status_code != 200:
            time.sleep(random.choice([5, 6, 7, 8, 9]) + random.random())
            crawl_blog_comment(max_id, blog_id)
        return resp.json()
    except:
        print(traceback.format_exc())
        pass


def save_weibo_comment(a: WeiboComment):
    sql = 'insert into weibo_comment(article_id, content,create_date,comment_user_id, like_count) values(%s, %s, %s, %s, %s)'
    try:
        db_cursor.execute(sql, (a.article_id, a.content, a.created_date, a.comment_user_id, a.like_count))
        db_conn.commit()
    except:
        print('insert weibo comment failure')
        print(traceback.format_exc())


def close_connection():
    if db_conn:
        db_conn.close()


def handle_comment(result_comments):
    for comment in result_comments:
        weibo_comment = WeiboComment()
        user = WeiboUser()
        try:
            user_ = comment.get('user')
            weibo_comment.article_id = comment.get('rootid')
            weibo_comment.content = comment.get('text')
            weibo_comment.created_date = comment.get('created_at')
            weibo_comment.comment_user_id = user_.get('id')
            weibo_comment.like_count = comment.get('like_counts')
            # print(weibo_comment.content)
            save_weibo_comment(weibo_comment)

            user.u_id = user_.get('id')
            user.u_name = user_.get('name')
            user.u_screen_name = user_.get('screen_name')
            user.u_signature = user_.get('description')
            user.u_follower_count = user_.get('followers_count')
            print(user.u_id, user.u_name, user.u_screen_name, user.u_signature, user.u_follower_count)

            save_weibo_user(user)
        except:
            print(traceback.format_exc())

        if 'comments' in comment.keys():
            handle_comment(comment.get('comments'))


def start_crawl_blog(start_page, end_page):
    for i in range(int(start_page), int(end_page)):
        try:
            print('weibo page: %s' % str(i))
            blog_list = crawl_blog(str(i))
        except:
            print(traceback.format_exc())
            break

        if 'cards' in blog_list.keys() and blog_list.get('cards'):
            for b in blog_list.get('cards'):
                article = WeiboArticle()
                try:
                    article.article_id = b.get('mblog').get('id')
                    article.content = b.get('mblog').get('text')
                    article.create_date = b.get('mblog').get('created_at')
                    article.comment_count = b.get('mblog').get('comments_count')
                    article.forward_count = b.get('mblog').get('reposts_count')
                    article.like_count = b.get('mblog').get('attitudes_count')

                    # print(article.content)
                    save_weibo_article(article)
                except:
                    print(traceback.format_exc())

                max_id = 0
                comment_page = 1
                while True:
                    print('crawl comment, page %s' % comment_page)
                    result_comment = crawl_blog_comment(max_id, article.article_id)

                    root_comments = result_comment.get('root_comments')
                    if root_comments:
                        handle_comment(root_comments)
                    else:
                        break

                    max_id = result_comment.get('max_id')
                    if max_id == 0:
                        break
                    comment_page += 1
                    time.sleep(random.choice([5, 6, 7, 8, 9]) + random.random())
        else:
            break

        time.sleep(random.choice([5, 6, 7, 8, 9]) + random.random())

    print('--' * 50)
    print()


if __name__ == '__main__':
    # start_crawl()
    # close_connection()
    try:
        start_page, end_page = argv[1], argv[2]
    except:
        print('Please input start page and end page, example: python weibo_miniprogram.py 1 10')
        sys.exit()

    try:
        start_crawl_blog(start_page, end_page)
        close_connection()
    except:
        print(traceback.format_exc())
    # start_crawl_blog(3, 4)
