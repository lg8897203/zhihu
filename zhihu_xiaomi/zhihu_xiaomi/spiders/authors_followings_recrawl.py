# -*- coding: utf-8 -*-
import json
from scrapy import Spider, Request
from pymongo import MongoClient


class AuthorsFollowingsRecrawlSpider(Spider):
    name = 'authors_followings_recrawl'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    #moclient = MongoClient ('localhost', 27017)
    moclient = MongoClient('192.168.7.16', 27017)
    db = moclient.iphonex
    db.collection_names(include_system_collections=False)
    posts = db.authors

    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    def start_requests(self):
        demos = self.posts.find(no_cursor_timeout=True).skip(15000)

        for post in demos:
            url_token = post['url_token']
            following_count = post['following_count']
            if following_count == 0 :
                if 'followings' in post.keys():
                    pass
                else:
                    self.db.authors.update({'url_token': url_token}, {"$pushAll": {"followings": []}})

            else:
                if 'followings' in post.keys():

                    result = len(post['followings'])
                    if (following_count - result) > 19:
                        print('继续爬!!')
                        yield Request(
                            self.follows_url.format(user=url_token, include=self.follows_query, limit=20, offset=result),
                            self.parse_follows)
                else:
                    print(url_token)
                    print('没有？')
                    #self.db.users_test.update({'url_token': url_token}, {"$pushAll": {"followings": []}})
                    yield Request(
                        self.follows_url.format(user=url_token, include=self.follows_query, limit=20, offset=0),
                        self.parse_follows)

            #yield Request(self.follows_url.format(user=url_token, include=self.follows_query, limit=20, offset=0),
            #             self.parse_follows)
        print('mongodb search finished!')
        demos.close()

    def parse_follows(self, response):
        results = json.loads(response.text)
        slug = results.get('paging').get('previous').split('/')[6]
        a = []
        if 'data' in results.keys():
            for result in results.get('data'):
                url_token = result.get('url_token')
                id = result.get('id')
                a.append(id)

            self.db.authors.update({'url_token': slug}, {"$pushAll": {"followings": a}})


        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,
                          self.parse_follows)



    def parse(self,response):
        pass

