# -*- coding: utf-8 -*-
from __future__ import print_function

import json

from scrapy import Spider, Request

from pymongo import MongoClient


class ActivitiesSpider(Spider):
    name = 'activities'
    allowed_domains = ['www.zhihu.com']
    moclient = MongoClient ('192.168.7.16', 27017)
    db = moclient.iphonex
    db.collection_names (include_system_collections=False)
    activities = db.activities


    url = 'https://www.zhihu.com/api/v4/members/{user}/activities?limit=7'
    url2 = 'https://www.zhihu.com/api/v4/members/{user}/activities?limit=7&after_id={after_id}&desktop=True'


    def start_requests(self):
        demos = self.activities.find(no_cursor_timeout=True).limit(4000)
        for post in demos:
            url_token = post['user_url_token']
            #finished = post['finished']
            if 'finished' in post.keys():
                finished = post['finished']
            else:
                finished = '0'

            if 'activities' in post.keys():
                activities = post['activities']
                last_time = activities[-1]['created_time']

                if len(activities) > 0 and last_time > 1500613200 and finished == '0':
                    print(url_token , 'Keep crawling!')

                    yield Request(self.url2.format(user=url_token, after_id = last_time), meta={'url_token': url_token},
                                  callback=self.parse_activities, dont_filter=True)

                if len(activities) > 0 and last_time < 1500613200 and finished == '0':
                    print(url_token, 'finished!')
                    self.activities.update({'user_url_token': url_token}, {"$set": {'finished': '1'}})


            else:
                print(url_token, 'None!')
                yield Request(self.url.format(user=url_token), meta={'url_token': url_token},
                              callback=self.parse_activities, dont_filter=True)

        demos.close()

    def parse_activities(self, response):
        results = json.loads(response.text)
        url_token = response.meta['url_token']
        #print(url_token)

        if 'data' in results.keys():
            if len(results.get('data')) > 0:
                #print(len(results.get('data')))
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
            #else:
            #    print(url_token,'finished!')

            #    self.activities.update({'user_url_token': url_token}, {"$set": {'finished': '1'}})

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            if time > 1500613200:
                yield Request(next_page, meta={'url_token': url_token}, callback=self.parse_activities)
            else:
                print(url_token, 'finished!')

                self.activities.update({'user_url_token': url_token}, {"$set": {'finished': '1'}})

        else:
            print(url_token, 'finished!')

            self.activities.update({'user_url_token': url_token}, {"$set": {'finished': '1'}})

    def parse(self, response):
        pass
