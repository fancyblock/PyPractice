from pymongo import MongoClient
import time
from sys import argv


g_store = None


# 用于管理存储相关的类
class Store(object):

    def __init__(self, address, port):
        self._client = MongoClient(address, port)
        self._db = self._client["milf_pic"]
        self._thread = self._db["thread_info"]
        self._pic_url = self._db["thread_pic_url"]
        self._pic_data = self._db["pic_data"]

    def get_specific_threads(self, keyword):
        return self._thread.find({"name": {"$regex": ".*" + keyword + ".*"}})

    def get_thread_pic_urls(self, tid):
        cursor = self._pic_url.find({"tid": tid})
        for val in cursor:
            return val["url"]

        return []

    def get_collection_doc_count(self, collection_name):
    	return self._db[collection_name].count()


if __name__ == "__main__":

    print("start")

    g_store = Store("localhost", 27017)

    curPicCount = g_store.get_collection_doc_count("pic_data")

    print("当前总图片数：" + str(curPicCount))
    print("--------------------------------------------------------")
    time.sleep(3.0)

    if len(argv) < 2:
        print("未添加参数")
    else:
        tt = g_store.get_specific_threads(argv[1])

        cnt = 0

        for t in tt:
            tid = t["tid"]
            name = t["name"]

            #print(name)
    
            urls = g_store.get_thread_pic_urls(tid)
    
            if urls:
                cnt += len(urls)

        print( str(cnt) + " picutres in all.")
