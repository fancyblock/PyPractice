import requests
from bs4 import BeautifulSoup
import os.path
import os


_baseUrl = "http://ss.postcc.us/"
_url = _baseUrl + "thread0806.php?fid=16"
_mainFolderName = "达盖尔的旗帜"


def Main():

    print("start")

    #　创建根目录
    if os.path.exists(_mainFolderName) == False:
        os.mkdir(_mainFolderName)

    try:
        pageData = requests.get(_url)

        if pageData.status_code == 200:
            pageSoup = BeautifulSoup(pageData.text)
            #pageSoup.
            threads = pageSoup.find_all(name = "tr", attrs={ "class":"tr3 t_one tac" })
            for thread in threads:
                dat = thread.find(name = "td", attrs = {"class":"tal"})
                a = 1

    except BaseException as be:
        print(str(be))


if __name__ == "__main__":
    Main()
