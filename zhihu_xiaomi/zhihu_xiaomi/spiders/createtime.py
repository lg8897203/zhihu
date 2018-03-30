# -*- coding: utf-8 -*-
from __future__ import print_function

import json

from scrapy import Spider, Request

from pymongo import MongoClient

class FollowingSpider(Spider):
    name = "createtime"
    allowed_domains = ["www.zhihu.com"]

    moclient = MongoClient ()
    moclient = MongoClient ('localhost', 27017)
    #moclient = MongoClient ('192.168.7.16', 27017)
    db = moclient.zhihuliker1
    db.collection_names (include_system_collections=False)
    posts = db.users

    url = 'https://www.zhihu.com/api/v4/members/{user}/activities?limit=5'
    url2 = 'https://www.zhihu.com/api/v4/members/{user}/activities?limit=20&after_id={after_id}&desktop=True'
    url3 = 'https://www.zhihu.com/api/v4/members/kumakuma-47/activities?limit=5'

    meta = {
        'dont_redirect': True,  # 禁止网页重定向
        'handle_httpstatus_list': [301, 302]  # 对哪些异常返回进行处理
    }

    def start_requests(self):
        for post in self.posts.find(no_cursor_timeout=True):
           name = post['url_token']
           print(name)
           yield Request(self.url.format(user=name),
                   self.parse_follows,dont_filter = True)
        self.posts.close()
        #yield Request(self.url3 , self.parse_follows, dont_filter=True)

    def parse_follows(self, response):
        results = json.loads(response.text)
        signal = True

        if 'data' in results.keys():
            for result in results.get('data'):
                type = result.get('verb')
                hash = result.get('actor').get('id')
                target_id = result.get('target').get('id')
                created_time = result.get ('created_time')
                print(type)
                print(target_id)
                if type == 'ANSWER_VOTE_UP' and target_id == 349117484:

                    print('I gotcha!!!')
                    self.db.users.update({'hash': hash}, {"$set": {"created_time": created_time}})
                    signal = False
                    break

                if created_time < 1489324248:
                    print('wo de cuo?')
                    signal = False
                    break

        if signal:
            if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
                next_page = results.get('paging').get('next')
                yield Request(next_page,
                              self.parse_follows)



    def parse(self,response):
        results = json.loads (response.text)
        for result in results.get('data'):
            print(result.get('verb'))
            print(result.get('target').get('id'))
            print(result.get('created_time'))

