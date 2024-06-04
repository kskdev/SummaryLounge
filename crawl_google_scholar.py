import os
import re
import time

import pandas as pd
import requests
import toml
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


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
        self.proxies = {
            "http" : self.conf["Crawler"]["ProxyHTTP"],
            "https": self.conf["Crawler"]["ProxyHTTPS"],
            }
        self.session = requests.session()
        self.retry_strategy = Retry(
            total=5,  # リトライ回数
            backoff_factor=1,  # リトライ間隔 (2回目は2秒、3回目は4秒...)
            status_forcelist=[429, 500, 502, 503, 504],  # リトライ対象のステータスコード
            allowed_methods=["HEAD", "GET", "OPTIONS"]  # リトライ対象のHTTPメソッド
        )
        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)
        self.session.mount("http://",  self.adapter)
        self.session.mount("https://", self.adapter)


    def fetch_html(self, target_URL):
        if self.conf["Crawler"]["UseProxy"]: self.session.proxies.update(self.proxies)

        try:
            response = self.session.get(target_URL, headers=self.header_dict)
            response.raise_for_status()  # HTTPエラーが発生した場合例外をスロー
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"[REQUEST FAILED]: {e}")


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
                print("[SCRAPE FAILED] Skip this Page.")

            time.sleep(self.sleep_sec)  # 紳士の対応
        print("Finished.")
        return self.paper_list_all_page


    def scrape_page(self, target_URL, is_debug=False):
        # ページ内のURLからHTMLを取得
        response = self.fetch_html(target_URL)
        self.soup = BeautifulSoup(response.content, "html.parser")
        self.paper_list_in_page = []
        if is_debug:
            with open("./debug.html", "w", encoding="UTF-8") as f:
                f.write(self.soup.prettify())

        # 各論文ごとに処理
        for _n, _paper in enumerate(self.soup.select(".gs_r")):
            print("targetInfo:{:>3}/{:<3}".format(_n, len(self.soup.select(".gs_r"))))

            # ----- Title
            try:
                title = _paper.select_one(".gs_rt a").get_text()  #  a を入れると， [PDF]や[HTML]という文字列が消せる
                for _delstr in self.del_str_list: title = title.replace(_delstr,"")
            except Exception as e:
                title = "-1"
            if is_debug:print("title     :",title)
            print("title     :",title)

            # ----- Authors
            try:
                name_list = [_a.get_text() for _a in _paper.select_one(".gs_a")]
                name_list.pop()  # 末尾要素は学会名．不要なので，pop()してリストの末尾を除去
                authors = "".join(name_list)
            except Exception as e:
                authors = "-1"
            if is_debug:print("authors   :",authors)

            # ----- Year
            try:
                year_text = _paper.select_one(".gs_a").get_text()
                year_pattern = r"\b[12][0-9]{3}\b"
                year = re.findall(year_pattern, year_text)[-1]
            except Exception as e:
                year = "0000"
            if is_debug:print("year      :",year)

            # ----- Conference
            try:
                tag_gs_a = _paper.select_one(".gs_a")
                conference = [_a.get_text() for _a in tag_gs_a if _a.find("a") is not None][-1]
            except Exception as e:
                conference = "-1"
            if is_debug:print("conference:",conference)

            # ----- Citations
            try:
                tag_gs_fl_list = [_a.get_text() for _a in _paper.select_one(".gs_fl") if _a.find("a") is None]
                citations_list = [_a for _a in tag_gs_fl_list if re.search("被引用数.*[0-9]+", _a)]
                if len(citations_list)==0: citations=0
                else                     : citations=citations_list[0].replace("被引用数: ","")
            except Exception as e:
                citations = -1
            if is_debug:print("citations :",citations)

            # ----- PDF
            try:
                print(_paper.select_one(".gs_or_ggsm"))
                if _paper.select_one(".gs_or_ggsm") is None:
                    pass
                else:
                    pdf_link = _paper.select_one(".gs_or_ggsm a").get("href")
            except Exception as e:
                pdf_link = "-1"
            print("PDF URL   :",pdf_link,"\n")

            paper_info = {
                "Title"     : title,
                "Author"    : authors,
                "Year"      : year,
                "Conference": conference,
                "Citations" : citations,
                "PDFLink"   : pdf_link,
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
    # print(crawler.fetch_html("https://www.yahoo.co.jp/"))
    paper_list = crawler.run_pages(query_word_list,is_debug=True)
    crawler.save_to_csv(paper_list,output_path)
