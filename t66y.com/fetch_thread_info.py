import requests
from bs4 import BeautifulSoup
import MongoStore
import winsound
import time


g_page_url = "http://ac.postcc.us/thread0806.php?fid=16"
g_base_url = "http://ac.postcc.us/"


# 获取页面中帖子信息
def fetch_thread_info(url, store):

    page_data = requests.get(url)
    new_thread_ids = []

    if page_data.status_code == 200:
        page_text = page_data.content.decode("gbk").encode("utf-8")
        page_soup = BeautifulSoup(page_text, "html.parser")
        threads = page_soup.find_all(name="tr", attrs={"class": "tr3 t_one tac"})

        for thread in threads:
            td = thread.find(name="td", attrs={"class": "tal"})

            if not td:
                continue

            ft_color = td.h3.a.font["color"] if td.h3.a.font else ""

            if ft_color != "green" and ft_color != "":
                continue

            thread_name = td.h3.a.string
            thread_url = td.h3.a["href"]
            thread_id = thread_url.split('/')[-1]
            thread_id = thread_id.split('.')[0]

            if thread_id == "read":
                continue

            if not store.has_thread(thread_id):
                new_thread_ids.append(thread_id)
                store.add_thread(thread_id, thread_name, thread_url)
                print("add thread info: " + thread_name)

    return new_thread_ids


# 获取帖子中图片信息
def fetch_pic_info(tid, store):
    url = g_base_url + store.get_thread_url(tid)
    page_data = requests.get(url)

    if page_data.status_code == 200:
        page_soup = BeautifulSoup(page_data.text, "html.parser")
        pic_info = page_soup.find_all(name="input", attrs={"type": "image"})

        url_list = []

        for i in pic_info:
            img_url = i["src"]
            ext_name = img_url.split('.')[-1]
            if ext_name == "gif" or ext_name == "GIF":
                continue

            url_list.append(img_url)

        if len(url_list) > 0:
            store.set_thread_urls(tid, url_list)
            print(tid + " collect " + str(len(url_list)) + " images.")


# 下载一张图片
def download_pic(store, url):
    try:
        pic_data = requests.get(url)

        if pic_data.status_code == 200:
            # 写数据库
            store.add_pic(url, pic_data.content)
            print("download " + url)

    except BaseException as be:
        print(str(be))


# 下载所有帖子中图片
def download_thread_pic(store, tid):
    try:
        urls = store.get_thread_pic_urls(tid)

        print("download " + tid)

        # 有缺文件或者一个都没有
        for i in range(len(urls)):
            url = urls[i]
            if not store.has_pic(url):
                download_pic(store, url)

    except BaseException as be:
        print("-------------------")
        print(str(be))
        time.sleep(1.0)
        winsound.Beep(3500, 1500)


def main():

    print("start")

    store = MongoStore.Store("127.0.0.1", 27017, "t66y_pic")

    all_new_thread_ids = []

    # 拉取帖子信息
    url = g_page_url

    while True:
        new_thread_ids = fetch_thread_info(url, store)

        if len(new_thread_ids) == 0:
            break
        else:
            if len(new_thread_ids) > 0:
                all_new_thread_ids.extend(new_thread_ids)

            page_data = requests.get(url)
            if page_data.status_code == 200:
                page_text = page_data.content.decode("gbk").encode("utf-8")
                page_soup = BeautifulSoup(page_text, "html.parser")
                next_page = page_soup.find(name="a", text="下一頁")
                if next_page:
                    url = g_base_url + next_page["href"]
                else:
                    break
            else:
                break

    # 拉帖子内图片信息
    for tid in all_new_thread_ids:
        fetch_pic_info(tid, store)

    # 下载帖子内图片数据
    for tid in all_new_thread_ids:
        download_thread_pic(store, tid)


def test():

    store = MongoStore.Store("127.0.0.1", 27017, "t66y_pic")

    all_threads = store.get_all_threads()

    cnt = 0
    img_cnt = 0

    for thread in all_threads:
        cnt = cnt + 1
        tid = thread["tid"]
        if "url" not in thread:
            print("find no url thread: " + tid)
            fetch_pic_info(tid, store)
            download_thread_pic(store, tid)
        else:
            urls = thread["url"]
            url_cnt = len(urls)
            img_cnt = img_cnt + url_cnt

    print(str(cnt))
    print("img count: " + str(img_cnt))


if __name__ == "__main__":
    main()
