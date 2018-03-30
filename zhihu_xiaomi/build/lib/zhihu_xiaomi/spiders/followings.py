# -*- coding: utf-8 -*-
import json
from scrapy import Spider, Request
from pymongo import MongoClient

class FollowingsSpider(Spider):
    name = 'followings'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    moclient = MongoClient()
    moclient = MongoClient ('localhost', 27017)
    #moclient = MongoClient('192.168.7.16', 27017)
    db = moclient.zhihu_xiaomi
    db.collection_names(include_system_collections=False)
    posts = db.users

    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        for post in self.posts.find().limit(6):
            url_token = post['url_token']
            yield Request(self.follows_url.format(user=url_token, include=self.follows_query, limit=20, offset=0),
                          self.parse_follows)

    def parse_follows(self, response):
        results = json.loads(response.text)
        slug = results.get('paging').get('previous').split('/')[6]
        a = []
        if 'data' in results.keys():
            for result in results.get('data'):
                url_token = result.get('url_token')
                id = result.get('id')
                a.append(id)

            self.db.users.update({'url_token': slug}, {"$pushAll": {"followings": a}})


        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,
                          self.parse_follows)



    def parse(self,response):
        results = json.loads (response.text)
        slug = results.get ('paging').get ('previous').split ('/')[6]
        print(slug)
        print(results.get('data')[2].get('url_token'))



    def parse(self, response):
        pass
