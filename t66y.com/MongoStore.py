from pymongo import MongoClient
import bson.binary


# 用于管理存储相关的类
class Store(object):

    def __init__(self, address, port, database_name):
        self._client = MongoClient(address, port)
        self._db = self._client[database_name]
        self._thread = self._db["thread_data"]
        self._pic = self._db["pic_data"]

    def has_thread(self, tid):
        cursor = self._thread.find({"tid": tid})

        if cursor.count() > 0:
            return True

        return False

    def add_thread(self, tid, thread_name, thread_url):
        self._thread.insert_one({"tid": tid, "name": thread_name, "thread_url": thread_url})

    def get_thread_url(self, tid):
        cursor = self._thread.find({"tid": tid})

        for val in cursor:
            return val["thread_url"]

        return None

    def get_thread_name(self, tid):
        cursor = self._thread.find({"tid": tid})

        for val in cursor:
            return val["name"]

        return None

    def set_thread_urls(self, tid, urls):
        self._thread.update_one({"tid": tid}, {"$set": {"url": urls}})

    def is_thread_need_download(self, tid):
        cursor = self._thread.find({"tid": tid})
        pic_done = True

        for val in cursor:
            if "pic_done" in val:
                pic_done = val["pic_done"]
            break

        return pic_done

    def set_thread_pic_done(self, tid):
        self._thread.update_one({"tid": tid}, {"$set": {"pic_done": True}})

    def get_all_threads(self):
        return self._thread.find({})

    def get_specific_threads(self, keyword):
        return self._thread.find({"name": {"$regex": ".*" + keyword + ".*"}})

    def get_thread_pic_urls(self, tid):
        cursor = self._thread.find({"tid": tid})
        for val in cursor:
            return val["url"]

        return []

    def has_pic(self, pic_url):
        cursor = self._pic.find({"url": pic_url})
        for val in cursor:
            return True

        return False

    def add_pic(self, raw_url, img_data):
        self._pic.insert_one({"url": raw_url, "data": bson.binary.Binary(img_data)})
