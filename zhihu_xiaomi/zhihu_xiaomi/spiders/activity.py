# -*- coding: utf-8 -*-
from __future__ import print_function

import json

from scrapy import Spider, Request

from pymongo import MongoClient


class ActivitySpider(Spider):
    name = 'activity'
    allowed_domains = ['www.zhihu.com']
    moclient = MongoClient ('192.168.7.16', 27017)
    db = moclient.iphonex
    db.collection_names (include_system_collections=False)
    activities = db.activities


    url = 'https://www.zhihu.com/api/v4/members/{user}/activities?limit=7'
    url2 = 'https://www.zhihu.com/api/v4/members/{user}/activities?limit=7&after_id={after_id}&desktop=True'


    def start_requests(self):
        demos = self.activities.find(no_cursor_timeout=True).limit(4000).skip(12000)
        for post in demos:

            url_token = post['user_url_token']

            yield Request(self.url2.format(user = url_token , after_id = 1522658330), meta={'url_token': url_token}, callback=self.parse_activities ,dont_filter = True)
        demos.close()

    def parse_activities(self, response):
        results = json.loads(response.text)
        url_token = response.meta['url_token']


        if 'data' in results.keys():
            if len(results.get('data')) > 0:
                time = results.get('data')[-1]['created_time']
                data = []
                for result in results.get('data'):
                    action_text = result['action_text']
                    created_time = result['created_time']
                    id = result['id']
                    verb = result['verb']
                    target_id = result['target']['id']
                    target_type = result['target']['type']
                    #print(created_time)

                    output = {'action_text':action_text,'created_time':created_time,'id':id,'verb':verb,'target_id':target_id,'target_type':target_type}
                    data.append(output)

                self.activities.update({'user_url_token': url_token}, {"$pushAll": {'activities': data}})


        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            if time > 1500613200:
                yield Request(next_page, meta={'url_token': url_token}, callback=self.parse_activities)

    def parse(self, response):
        pass
