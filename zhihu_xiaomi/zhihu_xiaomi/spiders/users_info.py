# -*- coding: utf-8 -*-
import json
from scrapy import Spider, Request, FormRequest
from zhihu_xiaomi.items import UserItem
from pymongo import MongoClient


class UsersInfoSpider(Spider):
    name = 'users_info'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    user_url = 'https://www.zhihu.com/api/v4/members/{uid}?include={include}'
    # query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    query2 = 'locations%2Cemployments%2Cgender%2Ceducations%2Cbusiness%2Cvoteup_count%2Cthanked_Count%2Cfollower_count%2Cfollowing_count%2Ccover_url%2Cfollowing_topic_count%2Cfollowing_question_count%2Cfollowing_favlists_count%2Cfollowing_columns_count%2Cavatar_hue%2Canswer_count%2Carticles_count%2Cpins_count%2Cquestion_count%2Ccommercial_question_count%2Cfavorite_count%2Cfavorited_count%2Clogs_count%2Cmarked_answers_count%2Cmarked_answers_text%2Cmessage_thread_token%2Caccount_status%2Cis_active%2Cis_force_renamed%2Cis_bind_sina%2Csina_weibo_url%2Csina_weibo_name%2Cshow_sina_weibo%2Cis_blocking%2Cis_blocked%2Cis_following%2Cis_followed%2Cmutual_followees_count%2Cvote_to_count%2Cvote_from_count%2Cthank_to_count%2Cthank_from_count%2Cthanked_count%2Cdescription%2Chosted_live_count%2Cparticipated_live_count%2Callow_message%2Cindustry_category%2Corg_name%2Corg_homepage%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    #moclient = MongoClient ()
    #moclient = MongoClient ('192.168.7.16', 27017)
    moclient = MongoClient ('localhost', 27017)
    db = moclient.zhihu_xiaomi
    db.collection_names (include_system_collections=False)
    posts = db.answers
    users = db.users

    def start_requests(self):
        for post in self.posts.find():
           uid = post['uid']
           if 'voters' in post.keys():
               voters = post['voters']
               voters.append(uid)
               print(len(post))
               for people in voters:
                   print(people)
                   yield Request(self.user_url.format(uid=people, include=self.query2), self.parse_user)

    def parse_user(self,response):
        results = json.loads(response.text)
        id = results['id']
        if self.users.find_one({"id": id}):
            print("这个ID有了！")
        else:
            item = UserItem()
            for field in item.fields:
                if field in results.keys():
                    item[field] = results.get(field)
            yield item

    def parse(self, response):
        pass
