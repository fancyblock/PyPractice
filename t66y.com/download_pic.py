import requests
from sys import argv
import winsound
import time
import MongoStore


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
def download_thread_pic(store, keyword):

    all_threads = store.get_specific_threads(keyword)

    try:
        for t in all_threads:
            tid = t["tid"]
            name = t["name"]
            urls = store.get_thread_pic_urls(tid)

            print("download " + name)

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


if __name__ == "__main__":

    print("start")

    if len(argv) < 2:
        print("未添加参数")
    else:
        # 数据库
        store = MongoStore.Store("127.0.0.1", 27017, "t66y_pic")

        # 下载帖子内图片
        download_thread_pic(store, argv[1])

        print("----------------------")
        print("图片下载完毕")
        print("")

        winsound.Beep(2500, 1500)
