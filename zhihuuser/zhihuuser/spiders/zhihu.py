# -*- coding: utf-8 -*-
import json

from scrapy import Spider, Request

from zhihuuser.items import UserItem


class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    # start_urls = ['http://www.zhihu.com/']
    start_user = 'excited-vczh'  # 轮子哥

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    # 关注他的人
    follower_query = 'data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
    follower_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'

    # 他关注的人
    followee_query = 'data%5B*%5D.answer_ count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
    followee_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'

    def start_requests(self):
        yield Request(url=self.user_url.format(user=self.start_user, include=self.user_query), callback=self.parse_user)
        yield Request(
            url=self.follower_url.format(user=self.start_user, include=self.follower_query, offset=0, limit=20),
            callback=self.parse_followers)
        yield Request(
            url=self.followee_url.format(user=self.start_user, include=self.followee_query, offset=0, limit=20),
            callback=self.parse_followees)

    def parse_user(self, response):
        result = json.loads(response.text)

        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)

        yield item

        # 递归爬取每个用户下的粉丝和用户关注的其他用户
        yield Request(url=self.follower_url.format(user=result.get('url_token'), include=self.follower_query, offset=0,
                                                   limit=20), callback=self.parse_followers)

        yield Request(url=self.followee_url.format(user=result.get('url_token'), include=self.followee_query, offset=0,
                                                   limit=20), callback=self.parse_followees)

    # # 关注他的人
    def parse_followers(self, response):
        results = json.loads(response.text)

        if 'data' in results.keys():
            for user in results.get('data'):
                token = user.get('url_token')
                yield Request(self.user_url.format(user=token, include=self.user_query), callback=self.parse_user)

        if 'paging' in results.get('paging') and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, callback=self.parse_followers)

    # 他关注的人
    def parse_followees(self, response):
        results = json.loads(response.text)

        if 'data' in results.keys():
            for user in results.get('data'):
                token = user.get('url_token')
                yield Request(self.user_url.format(user=token, include=self.user_query), callback=self.parse_user)

        if 'paging' in results.get('paging') and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, callback=self.parse_followees)
