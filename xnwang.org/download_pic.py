from pymongo import MongoClient
import requests
import bson.binary
import os
from sys import argv
import winsound
import time


g_store = None
site_base_url = "http://xnwang.org/"


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

    def has_pic(self, raw_url):
        cursor = self._pic_data.find({"url": raw_url})
        for val in cursor:
            return True

        return False

    def add_pic(self, raw_url, img_data):
        self._pic_data.insert_one({"url": raw_url, "data": bson.binary.Binary(img_data)})


def download_pic(raw_url, url):
    try:
        pic_data = requests.get(url)

        if pic_data.status_code == 200:
            # 写数据库
            g_store.add_pic(raw_url, pic_data.content)
            print("download " + url)
    except BaseException as be:
        print(str(be))


# 下载所有帖子中图片
def download_thread_pic(keyword):

    all_threads = g_store.get_specific_threads(keyword)

    try:
        for t in all_threads:
            tid = t["tid"]
            name = t["name"]
            urls = g_store.get_thread_pic_urls(tid)

            pending_download_list = []
            pending_file_name = []

            print("download " + name)

            # 有缺文件或者一个都没有
            for i in range(len(urls)):
                url = urls[i]
                part = url.split("/")
                file_name = part[-1]
                pending_file_name.append(file_name)
                if not g_store.has_pic(url):
                    pending_download_list.append(i)

            for index in pending_download_list:
                raw_url = urls[index]
                download_pic(raw_url, site_base_url + raw_url)
    except BaseException as be:
        print("-------------------")
        print(str(be))
        time.sleep(1.0)
        winsound.Beep(3500, 1500)


if __name__ == "__main__":

    print("start")

    if len(argv) < 2:
        print("未添加参数")
    else:
        # 数据库
        g_store = Store("localhost", 27017)

        # 下载帖子内图片
        download_thread_pic(argv[1])

        print("----------------------")
        print("图片下载完毕")
        print("")

        winsound.Beep(2500, 1500)
