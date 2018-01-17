import requests
from bs4 import BeautifulSoup
from MongoStore import Store


g_store = None
g_page_url = "http://dd.itbb.men/thread0806.php?fid=16"         # 达盖尔的旗帜板块


if __name__ == "__main__":

    print("start")

    # 数据库
    g_store = Store("localhost", 27017, "t66y_pic")

    # 拉取页面帖子信息
    new_thread_ids = fetch_thread_info()

    print("----------------------")
    print("帖子信息更新完毕,新增" + str(len(new_thread_ids)) + "个帖子")
    print("")

    print("----------------------")
    print("帖子内图片信息更新完毕")
    print("")
