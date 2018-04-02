# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import json
from pymongo import MongoClient


class AnswersSpider(Spider):
    flag = 0
    name = 'answers'
    allowed_domains = ['www.zhihu.com']
    answer_url = 'https://www.zhihu.com/api/v4/questions/{qid}/answers?include=data%5B*%5D.is_normal%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={offset}&limit={limit}&sort_by=default'
    #moclient = MongoClient ('192.168.7.16', 27017)
    moclient = MongoClient ('localhost', 27017)
    db = moclient.iphonex
    db.collection_names (include_system_collections=False)
    posts = db.questions
    #count = posts.count()
    #iter = int(count/100)
    #print(iter)

    def start_requests(self):
        # for i in range(0, 11):
        #     print(i)
        #
        #     for post in self.posts.find().limit(100).skip(i * 100):
        #         qid = post['qid']
        #         yield Request(self.answer_url.format(qid=qid, limit=20, offset=0),
        #                  self.parse)
        demos = self.posts.find(no_cursor_timeout=True)
        for post in demos:
            qid = post['target']['id']
            yield Request(self.answer_url.format(qid=qid, limit=5, offset=0),
                             self.parse)
        print('mongodb search finished!')
        demos.close()

    def parse(self, response):
        results = json.loads(response.text)

        if results['data']:
            self.db.answers.insert(results['data'])


        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, self.parse)
