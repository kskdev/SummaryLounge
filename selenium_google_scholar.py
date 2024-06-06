import os
import re
import time

import toml
import urllib.parse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

class PaperCrawler:
    def __init__(self) -> None:
        with open("./config.toml","r",encoding="UTF-8") as f: self.conf=toml.load(f)

        self.header_dict = { "User-Agent": self.conf["Crawler"]["UserAgent"]}
        self.sleep_sec = int(self.conf["Crawler"]["IntervalSec"])
        self.max_page_num = int(self.conf["Crawler"]["MaxPageNum"])
        self.page_list = []
        self.target_URL = ""
        self.del_str_list = self.conf["Crawler"]["RemoveList"]

        self.options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome()


    def collect_html(self, target_URL, save_dir="./Result/"):
        query_name = urllib.parse.urlparse(target_URL).query
        query_name = query_name.replace("&hl=ja&q=","-").replace("start=0-","").replace("+","_")
        self.driver.get(target_URL)
        time.sleep(self.sleep_sec)

        self.page_list = []
        for _page in [_i for _i in range(1,self.max_page_num+1)]:
            # ページ遷移
            time.sleep(self.sleep_sec)
            if _page>1: self.driver.find_element(By.LINK_TEXT, str(_page)).click()

            # 保存先設定
            self.current_URL = self.driver.current_url
            self.page_html   = self.driver.page_source
            savename = "page{:>03}_{}.html".format(_page, query_name)
            os.makedirs(save_dir, exist_ok=True)
            savepath = os.path.join(save_dir,savename)

            # 保存
            soup = BeautifulSoup(self.page_html, "html.parser")
            with open(savepath, "w", encoding="UTF-8") as f: f.write(soup.prettify())
            print("Saved HTML: ", savepath)

        self.driver.quit()


if __name__ == "__main__":
    query_word_list = ["attention","all","you","need"]

    output_dir  = "./Result"
    output_name = "paperlist_{}.csv".format("-".join(query_word_list))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir,output_name)


    keyword  = "+".join(query_word_list)
    page_num = 0
    target_URL = f"https://scholar.google.com/scholar?start={page_num}&hl=ja&q={keyword}"

    crawler = PaperCrawler()
    crawler.collect_html(target_URL)
