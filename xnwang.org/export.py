from pymongo import MongoClient
import bson.binary
import os
from sys import argv


g_store = None
folder_name = "milf_picture"


# 用于管理存储相关的类
class Store(object):

    def __init__(self, address, port):
        self._client = MongoClient(address, port)
        self._db = self._client["milf_pic"]
        self._thread = self._db["thread_data"]
        self._pic_data = self._db["pic_data"]

    def get_specific_threads(self, keyword):
        return self._thread.find({"name": {"$regex": ".*" + keyword + ".*"}})

    def get_thread_pic_urls(self, tid):
        cursor = self._thread.find({"tid": tid})
        for val in cursor:
            return val["url"]

        return []

    def get_pic(self, raw_url):
        cursor = self._pic_data.find({"url": raw_url})
        for val in cursor:
            return val["data"]

        return None


def export(keyword):

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    all_threads = g_store.get_specific_threads(keyword)

    for t in all_threads:
        tid = t["tid"]
        name = t["name"]
        urls = g_store.get_thread_pic_urls(tid)

        thread_folder_name = folder_name + "/" + name.replace("*", "-") + "[" + tid + "]"

        if not os.path.exists(thread_folder_name):
            os.mkdir(thread_folder_name)
            print("创建目录: " + name)

        for url in urls:
            pic_data = g_store.get_pic(url)
            if pic_data:
                part = url.split("/")
                pic_file_name = part[-1]
                file = open( thread_folder_name + "/" + pic_file_name, "wb")
                file.write(pic_data)
                file.close()


if __name__ == "__main__":

    print("start")

    if len(argv) < 2:
        print("未添加参数")
    else:
        # 数据库
        g_store = Store("localhost", 27017)

        # 下载帖子内图片
        export(argv[1])

        print("----------------------")
        print("图片导出完毕")
        print("")
