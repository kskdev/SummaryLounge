import os
import re
import time

import pandas as pd
import requests
import toml
from bs4 import BeautifulSoup

class PaperCrawler:
    def __init__(self) -> None:
        with open("./config.toml","r",encoding="UTF-8") as f: self.conf=toml.load(f)

        self.header_dict = { "User-Agent": self.conf["Crawler"]["UserAgent"]}
        self.sleep_sec = self.conf["Crawler"]["IntervalSec"] 
        self.max_page_num = self.conf["Crawler"]["MaxPageNum"] 
        self.pages_list= [page*10 for page in range(self.max_page_num)]
        self.paper_list_all_page = []
        self.target_URL = ""
        self.del_str_list = self.conf["Crawler"]["RemoveList"] 

    def run_pages(self, keyword_list, is_debug=False):
        for _page_num in self.pages_list:
            # URL 作成
            keyword  = "+".join(keyword_list)
            self.target_URL = f"https://scholar.google.com/scholar?start={_page_num}&hl=ja&q={keyword}"
            print("[TARGET URL] ", self.target_URL)

            # ページ内スクレイピング
            try:
                paper_list_one_page = self.scrape_page(self.target_URL, is_debug)
                self.paper_list_all_page.extend(paper_list_one_page)
            except:
                print("[SCRAPE FAILED.]")
                return self.paper_list_all_page

            # DDoSしない
            time.sleep(self.sleep_sec)
        print("Finished.")
        return self.paper_list_all_page

    def scrape_page(self, target_URL, is_debug=False):
        # ページ内のURLからHTMLを取得
        response = requests.get(target_URL, headers=self.header_dict)
        print(response)
        self.soup = BeautifulSoup(response.content, "html.parser")
        self.paper_list_in_page = []

        # 各論文ごとに処理
        for _n, _paper in enumerate(self.soup.select(".gs_ri")):
            title = _paper.select_one(".gs_rt").get_text()
            for _delstr in self.del_str_list: title = title.replace(_delstr,"")
            if is_debug:print("title     :",title)

            tag_gs_a = _paper.select_one(".gs_a")

            # <a href> の中の人の名前だけ取得
            name_list = [_a.get_text() for _a in tag_gs_a]
            name_list.pop()  # 末尾要素は学会名．なので，pop()でリストから除去
            authors = "".join(name_list)
            if is_debug:print("authors   :",authors)

            year_text = tag_gs_a.get_text()
            year_pattern = r"\b[12][0-9]{3}\b"
            year = re.findall(year_pattern, year_text)[-1]
            if is_debug:print("year      :",year)

            conference = [_a.get_text() for _a in tag_gs_a if _a.find("a") is not None][-1]
            if is_debug:print("conference:",conference)

            tag_gs_fl_list = [_a.get_text() for _a in _paper.select_one(".gs_fl") if _a.find("a") is None]
            citations_list = [_a for _a in tag_gs_fl_list if re.search("被引用数.*[0-9]+", _a)]
            if len(citations_list)==0: citations=0
            else                     : citations=citations_list[0].replace("被引用数: ","")
            if is_debug:print("citations :",citations,"\n")

            # try: pdf_url = _paper.select_one(".gs_or_ggsm a")["href"]
            # except TypeError: pdf_url = ""
            # if is_debug:print("target URL:",pdf_url)

            paper_info = {
                "Title"     : title,
                "Author"    : authors,
                "Year"      : year,
                "Conference": conference,
                "Citations" : citations,
                # "URL"       : pdf_url,
            }
            self.paper_list_in_page.append(paper_info)
        return self.paper_list_in_page 


    def save_to_csv(self, paper_dict_list, filename="paper_list.csv"):
        df = pd.DataFrame(paper_dict_list)
        df.to_csv(filename, index=False, encoding="UTF-8")


if __name__ == "__main__":

    query_word_list = ["attention","all","you","need"]

    output_dir  = "./Result"
    output_name = "paperlist_{}.csv".format("-".join(query_word_list))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir,output_name)

    crawler = PaperCrawler()
    paper_list = crawler.run_pages(query_word_list,is_debug=False)
    crawler.save_to_csv(paper_list,output_path)