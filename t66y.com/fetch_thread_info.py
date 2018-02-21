import requests
from bs4 import BeautifulSoup
import MongoStore


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
        pic_info = page_soup.find(name="div", attrs={"class":"tpc_content do_not_catch"})
        table = pic_info.find_all(name="table")
        if table:
            pic_info = table[0]

        all_pic_urls = pic_info.find_all(name="input", attrs={"type": "image"})
        url_list = []

        for i in all_pic_urls:
            img_url = i["src"]
            ext_name = img_url.split('.')[-1]
            if ext_name == "gif" or ext_name == "GIF":
                continue

            url_list.append(img_url)

        if len(url_list) > 0:
            store.set_thread_urls(tid, url_list)
            print( tid + " collect " + str(len(url_list)) + " images.")


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
            all_new_thread_ids.append(new_thread_ids)
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
    all_threads = store.get_all_threads()

    for thread in all_threads:
        if "url" not in thread:
            fetch_pic_info(thread["tid"], store)


if __name__ == "__main__":
    main()
