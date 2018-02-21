import requests
from sys import argv
import winsound
import time
import MongoStore


def download_pic(header, store, url):
    try:
        pic_data = requests.get(url, headers= header)

        if pic_data.status_code == 200:
            # 写数据库
            store.add_pic(url, pic_data.content)
            print("download " + url)

    except BaseException as be:
        print(str(be))


# 下载所有帖子中图片
def download_thread_pic(header, store, keyword):

    all_threads = store.get_specific_threads(keyword)

    try:
        for t in all_threads:
            tid = t["tid"]
            name = t["name"]
            urls = store.get_thread_pic_urls(tid)

            print("download " + tid)

            # 有缺文件或者一个都没有
            for i in range(len(urls)):
                url = urls[i]
                if not store.has_pic(url):
                    download_pic(header, store, url)

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

        header = {}
        header["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        header["Accept-Encoding"] = "gzip, deflate"
        header["Accept-Language"] = "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"
        header["Cache-Control"] = "max-age=0"
        header["Connection"] = "keep-alive"
        header["Upgrade-Insecure-Requests"] = "1"
        header["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"

        # 下载帖子内图片
        download_thread_pic(header, store, argv[1])

        print("----------------------")
        print("图片下载完毕")
        print("")

        winsound.Beep(2500, 1500)
