import requests
from bs4 import BeautifulSoup
import os.path
import os
import threading
import time


_baseUrl = "http://ss.wedid.us/"
_url = _baseUrl + "thread0806.php?fid=16"
_mainFolderName = "达盖尔的旗帜"

_filterThreadTitle = ["其實发图很簡單", "举报贴", "为什么你的帖子没有得到评分", "各类图片上传的图床", "图区禁止使用下列图床", "自拍区发帖前必读", "普通主題禁止三連發"]


class ThreadInfo:
    def __init__(self):
        self._title = None
        self._url = None


class PageInfo:
    def __init__(self):
        self._threads = []
        self._nextUrl = None


# 下载图片
def download_pic(url, folder_path):
    try:
        picData = requests.get(url)

        if picData.status_code == 200 and len(picData.content) > 10240:  # 大于10k的图才会存
            fileName = url[url.rfind('/') + 1:]
            file = open(folder_path + "/" + fileName, "wb")
            file.write(picData.content)
            file.close()
    except:
        pass


# 下载一个帖子里的图
def fetch_thread(title, url):
    print("fetch thread " + title)
    folder_path = _mainFolderName + "/" + title
    if os.path.exists(folder_path):
        return

    os.mkdir(folder_path)

    try:
        threadData = requests.get(_baseUrl + url)

        if threadData.status_code == 200:
            threadHtmlText = threadData.text
            threadSoup = BeautifulSoup(threadHtmlText, "html.parser")
            imageInputs = threadSoup.find_all(name="input", attrs={"type":"image"})

            _downloadCount = len( imageInputs )

            for imgInput in imageInputs:
                imgSrc = imgInput["src"]

                if imgSrc != None:
                    # 下载图片
                    t = threading.Thread(target=download_pic, args=[imgSrc, folder_path])
                    t.start()

            time.sleep(1)

    except BaseException as be:
        print(str(be))


# 下载一个页面里所有的帖子
def fetch_threads(url):
    try:
        pageData = requests.get(_url)

        if pageData.status_code == 200:
            pageHtmlText = pageData.content.decode("GBK").encode("utf-8")
            pageSoup = BeautifulSoup(pageHtmlText, "html.parser")
            threads = pageSoup.find_all(name="tr", attrs={"class": "tr3 t_one tac"})
            page_info = PageInfo()
            for thread in threads:
                tInfo = thread.find(name="td", attrs={"class": "tal"})

                if tInfo == None:
                    continue

                threadUrl = tInfo.h3.a["href"]

                if "htm_data" not in threadUrl:
                    continue

                threadTitle = tInfo.h3.a.string

                # 过滤掉部分帖子
                passThread = False
                for filterName in _filterThreadTitle:
                    if filterName in threadTitle:
                        passThread = True
                        break

                if passThread:
                    continue

                # 转换掉帖子名里的/
                threadTitle = threadTitle.replace('/', '-')
                # 删除帖子名里的？
                threadTitle = threadTitle.replace('?', '-')

                thread_info = ThreadInfo()
                thread_info._title = threadTitle
                thread_info._url = threadUrl

                page_info._threads.append(thread_info)

            # 查看是否有下一页
            nextPage = pageSoup.find(name="a", text="下一頁")
            if nextPage != None:
                page_info._nextUrl = _baseUrl + nextPage["href"]

            return page_info

    except BaseException as be:
        print(str(be))

    return None


def main():

    print("start")

    #　创建根目录
    if os.path.exists(_mainFolderName) == False:
        os.mkdir(_mainFolderName)

    page_info = fetch_threads(_url)

    while page_info != None:
        for pi in page_info._threads:
            fetch_thread(pi._title, pi._url)    # 抓取每个帖子里的图片们

        if page_info._nextUrl != None:
            page_info = fetch_threads(page_info._nextUrl)   # 下一页
        else:
            page_info = None


if __name__ == "__main__":
    main()
