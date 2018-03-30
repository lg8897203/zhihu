# -*- coding: utf-8 -*-

from pymongo import MongoClient

moclient = MongoClient()
#moclient = MongoClient ('192.168.7.16', 27017)
moclient = MongoClient('localhost', 27017)
db = moclient.zhihu_xiaomi
db.collection_names(include_system_collections=False)
coll = db.comments_copy
tmp_coll = db.cid_dups

for i in tmp_coll.find({"value": {"$gt":1}}):
    id = i['_id']
    value = i['value']
    for j in coll.find({"cid": id}, {"cid":1}):
        remove_id = j['cid']
        print(remove_id)
        count = coll.count({"cid": remove_id})
        if count > 1:
            result = coll.delete_one({"cid": remove_id})
