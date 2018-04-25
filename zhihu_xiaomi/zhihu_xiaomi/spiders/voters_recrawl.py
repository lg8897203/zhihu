# -*- coding: utf-8 -*-
import json
from scrapy import Spider, Request
from pymongo import MongoClient

class FollowingsVotersSpider(Spider):
    name = 'voters_recrawl'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    moclient = MongoClient ('localhost', 27017)
    #moclient = MongoClient('192.168.7.16', 27017)
    db = moclient.iphonex
    db.collection_names(include_system_collections=False)
    posts = db.answers

    voter_url = 'https://www.zhihu.com/api/v4/answers/{aid}/voters?include=data%5B*%5D.answer_count%2Carticles_count%2Cfollower_count%2Cgender%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={offset}&limit={limit}'

    def start_requests(self):
        demos = self.posts.find(no_cursor_timeout=True).limit(5000).skip(20000)

        for post in demos:
            aid = post['id']
            voteup_count = post['voteup_count']
            if voteup_count == 0 :
                if 'voters' in post.keys():
                    pass
                else:
                    self.db.answers.update({'id': int(aid)}, {"$pushAll": {"voters": []}})

            else:
                if 'voters' in post.keys():

                    result = len(post['voters'])
                    if (voteup_count - result) > 9:
                        print('继续爬!!')
                        yield Request(
                            self.voter_url.format(aid=aid , limit=10, offset=result),
                                     self.parse_follows)
                else:
                    print(aid)
                    print('没有？')
                    #self.db.users_test.update({'url_token': url_token}, {"$pushAll": {"followings": []}})
                    yield Request(
                        self.voter_url.format(aid=aid, limit=10, offset=0),
                        self.parse_follows)

            #yield Request(self.follows_url.format(user=url_token, include=self.follows_query, limit=20, offset=0),
            #             self.parse_follows)
        print('mongodb search finished!')
        demos.close()

    def parse_follows(self, response):
        results = json.loads(response.text)
        aid = results.get('paging').get('previous').split('/')[6]
        a = []
        if 'data' in results.keys():
            for result in results.get('data'):
                uid = result.get('id')
                a.append(uid)
            self.db.answers.update({'id': int(aid)}, {"$pushAll": {"voters": a}})

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, self.parse_follows)



    def parse(self,response):
        pass

