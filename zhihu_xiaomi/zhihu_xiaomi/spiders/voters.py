# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import json
from pymongo import MongoClient
from zhihu_xiaomi.items import ZhihuXiaomiItem

class AnswersSpider(Spider):
    name = 'voters'
    allowed_domains = ['www.zhihu.com']
    voter_url = 'https://www.zhihu.com/api/v4/answers/{aid}/voters?include=data%5B*%5D.answer_count%2Carticles_count%2Cfollower_count%2Cgender%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={offset}&limit={limit}'
    #moclient = MongoClient ()
    #moclient = MongoClient ('192.168.7.16', 27017)
    moclient = MongoClient ('localhost', 27017)
    db = moclient.zhihu_maoyizhan
    db.collection_names (include_system_collections=False)
    posts = db.voters
    aid = '349117484'

    def start_requests(self):
        yield Request(self.voter_url.format(aid=self.aid, limit=10, offset=0),
                      self.voter_parse)
        # for post in self.posts.find():
        #     aid = post['aid']
        #     voteup_count = post['voteup_count']
        #     #voters
        #     if voteup_count > 0:
        #         yield Request(self.voter_url.format(aid=aid, limit=10, offset=0),
        #                       self.voter_parse)

    def voter_parse(self, response):
        results = json.loads(response.text)
        self.db.voters.insert(results['data'])

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, self.voter_parse)