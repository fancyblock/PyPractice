from pymongo import MongoClient


# 用于管理存储相关的类
class Store(object):

    def __init__(self, address, port, database_name):
        self._client = MongoClient(address, port)
        self._db = self._client[database_name]
        self._thread = self._db["thread_info"]
        self._pic_url = self._db["thread_pic_url"]
        self._pic_data = self._db["pic_data"]

    def has_thread(self, thread_id):
        cursor = self._thread.find({"tid": thread_id})

        if cursor.count() > 0:
            return True

        return False

    def add_thread(self, thread_id, thread_name, thread_url):
        self._thread.insert_one({"tid": thread_id, "name": thread_name, "url": thread_url})

    def get_thread_url(self, thread_id):
        cursor = self._thread.find({"tid": thread_id})

        for val in cursor:
            return val["url"]

        return None

    def get_thread_name(self, thread_id):
        cursor = self._thread.find({"tid": thread_id})

        for val in cursor:
            return val["name"]

        return None

    def get_all_threads(self):
        return self._thread.find({})

    def get_specific_threads(self, keyword):
        return self._thread.find({"name": {"$regex": ".*" + keyword + ".*"}})

    def has_thread_pics(self, tid):
        cursor = self._pic_url.find({"tid": tid})

        if cursor.count() > 0:
            return True

        return False

    def save_thread_pics(self, tid, pic_url_list):
        self._pic_url.insert_one({"tid": tid, "url": pic_url_list})

    def has_pic(self, pic_url):
        #TODO
        return False