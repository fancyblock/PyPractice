import requests
from sys import argv
import winsound
import time
import MongoStore


def download_pic(proxy, store, url):
    try:
        pic_data = requests.get(url, proxies= proxy)

        if pic_data.status_code == 200:
            # 写数据库
            store.add_pic(url, pic_data.content)
            print("download " + url)

            return True
        else:
            print(str(pic_data.status_code))

            if pic_data.status_code == 404:
                return True

    except BaseException as be:
        exp_str = str(be)
        print(str(be))

        if "certificate verify failed" in exp_str:
            return True

    return False


# 下载所有帖子中图片
def download_thread_pic(proxy, store, keyword):

    all_threads = None

    if keyword:
        all_threads = store.get_specific_threads(keyword)
    else:
        all_threads = store.get_all_threads()

    try:
        for t in all_threads:
            tid = t["tid"]

            if not store.is_thread_need_download(tid):
                continue

            urls = store.get_thread_pic_urls(tid)

            print("download " + tid + "  [" + str(len(urls)) + "]")

            # 有缺文件或者一个都没有
            pending_urls = []
            for i in range(len(urls)):
                url = urls[i]
                if not store.has_pic(url):
                    pending_urls.append(url)

            pending_url_count = len(pending_urls)

            print("need download " + str(pending_url_count) + " pictures.")

            if pending_url_count > 0:
                result = True
                for u in pending_urls:
                    result = download_pic(proxy, store, u) and result

                if result:
                    store.set_thread_pic_done(tid)

            else:
                store.set_thread_pic_done(tid)

    except BaseException as be:
        print("-------------------")
        print(str(be))
        time.sleep(1.0)
        winsound.Beep(3500, 1500)


if __name__ == "__main__":

    print("start")

    # 数据库
    store = MongoStore.Store("127.0.0.1", 27017, "t66y_pic")

    proxy = {"http": "http://127.0.0.1:1080", "https": None}

    if len(argv) < 2:
        download_thread_pic(proxy, store, None)
    else:
        download_thread_pic(proxy, store, argv[1])

    print("----------------------")
    print("图片下载完毕")
    print("")

    winsound.Beep(2500, 1500)
