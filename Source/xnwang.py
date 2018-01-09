from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import time


g_header = {}
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

    def has_thread_pics(self, tid):
        cursor = self._pic_url.find({"tid": tid})

        if cursor.count() > 0:
            return True

        return False

    def save_thread_pics(self, tid, pic_url_list):
        self._pic_url.insert_one({"tid": tid, "url": pic_url_list})


# 获取页面里的帖子
def collect_thread(page_url):
    try:
        page_data = requests.get(page_url, headers=g_header)

        if page_data.status_code == 200:
            page_text = page_data.content
            page_soup = BeautifulSoup(page_text, "html.parser")
            threads = page_soup.find_all(name="a", attrs={"class": "s xst", "onclick": "atarget(this)"})
            new_thread_ids = []

            for thread in threads:
                thread_name = thread.string
                thread_url = thread["href"]
                thread_id = thread_url.split("thread-")[1].split(".")[0].split("-")[0]

                if not g_store.has_thread(thread_id):
                    g_store.add_thread(thread_id, thread_name, thread_url)
                    new_thread_ids.append(thread_id)
                    print(thread_name + "  added. [" + thread_id + "]" )

            return new_thread_ids
        else:
            print("get page failed. " + page_url)

    except BaseException as be:
        print(str(be))

    return []


# 获取页面
def fetch_thread_info():
    # 获取页面
    _page_urls = ["forum-40-", "forum-41-", "forum-42-", "forum-43-", "forum-44-", "forum-45-", "forum-49-", "forum-2-"]

    new_thread_id = []
    for i in range(len(_page_urls)):
        base_url = site_base_url + _page_urls[i]

        page_index = 1
        while True:
            thread_ids = collect_thread(base_url + str(page_index) + ".html")
            page_index += 1
            if len(thread_ids) > 0:
                new_thread_id.extend(thread_ids)
                time.sleep(0.1)
            else:
                break

    return new_thread_id


# 获取页面内图片下载地址 
def collect_thread_pics(tid, thread_url):
    try:
        page_data = requests.get(thread_url, headers=g_header)

        if page_data.status_code == 200:
            page_text = page_data.content
            page_soup = BeautifulSoup(page_text, "html.parser")
            pic_url = page_soup.find_all(name="ignore_js_op")

            url_list = []

            for raw_pic_info in pic_url:
                try:
                    final_url = raw_pic_info.img["file"]
                    url_list.append(final_url)
                except:
                    pass

            if len(url_list) > 0:
                # 存到数据库
                g_store.save_thread_pics(tid, url_list)
                thread_name = g_store.get_thread_name(tid)
                print(thread_name + "\t\t" + str(len(url_list)) + "张图片url已保存 ["+ tid +"]")
            else:
                thread_name = g_store.get_thread_name(tid)
                print(thread_name + "  一张图片也没有 [" + tid + "]")
        else:
            print("get page pic failed. " + thread_url)
            
    except BaseException as be:
        print(str(be) + "   [" + tid + "]")


# 获取帖子内图片信息
def fetch_thread_pic_info(thread_ids):

    for tid in thread_ids:
        # 是否已经获取过
        if not g_store.has_thread_pics(tid):
            url = g_store.get_thread_url(tid)
            collect_thread_pics(tid, url)


# 下载所有帖子中图片
def download_thread_pic():
    all_threads = g_store.get_all_threads()

    for t in all_threads:
        pass


if __name__ == "__main__":

    print("start")

    # 标准header
    g_header = {}
    g_header["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    g_header["Accept-Encoding"] = "gzip, deflate"
    g_header["Accept-Language"] = "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"
    g_header["Cache-Control"] = "max-age=0"
    g_header["Connection"] = "keep-alive"
    g_header["Referer"] = "http://xnwang.org/"
    g_header["Upgrade-Insecure-Requests"] = "1"
    g_header["Cookie"] = """UM_distinctid=1608ddc94de6a3-09e7feee1c7152-b7a103e-1fa400-1608ddc94dfadb; gatz_2132_saltkey=Cy7uLLw6; gatz_2132_lastvisit=1514903378; gatz_2132_atarget=1; gatz_2132_auth=aff6W88QaKI7NzEiEtLhYCEoENdYRGAk2nyqFg7oErSwh4fAsB5dP4vblabgJEXm3sM4%2B7nVS4XMyh7bsUJcxEXLqiA; gatz_2132_lastcheckfeed=279662%7C1514907001; gatz_2132_smile=1D1; gatz_2132_nofavfid=1; gatz_2132_member_login_status=1; PHPSESSID=tt00rnimnd6drds1nomnchee15; gatz_2132_ulastactivity=5c0b4MpedJq8uXVjyiouUjNz%2Bm2qzPLMxLyxVFas8Vm1KXSBJ3k5; CNZZDATA1271567903=933849855-1514205120-http%253A%252F%252Fxnwang.org%252F%7C1515252771; gatz_2132_sid=sR77Jl; gatz_2132_lip=116.234.111.239%2C1515254125; gatz_2132_sendmail=1; gatz_2132_noticeTitle=1; gatz_2132_st_t=279662%7C1515257465%7C2709520b801eb238e0310b6f0145de98; gatz_2132_forum_lastvisit=D_42_1515253161D_44_1515257465; gatz_2132_visitedfid=2D44D42; gatz_2132_st_p=279662%7C1515257491%7C244946694665e5e204f31679590d6488; gatz_2132_viewid=tid_144828; gatz_2132_lastact=1515257620%09forum.php%09ajax"""
    g_header["Host"] = "xnwang.org"
    g_header["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"

    # 数据库
    g_store = Store("localhost", 27017)

    # 拉取页面帖子信息
    new_thread_ids = fetch_thread_info()

    print("----------------------")
    print("帖子信息更新完毕,新增" + str(len(new_thread_ids)) + "个帖子")
    print("")
    time.sleep(3)

    # 拉取帖子内图片信息
    fetch_thread_pic_info(new_thread_ids)

    print("----------------------")
    print("帖子内图片信息更新完毕")
    print("")
    time.sleep(3)

    # 下载帖子内图片
    download_thread_pic()

    print("----------------------")
    print("所有帖子图片下载完毕")
    print("")
