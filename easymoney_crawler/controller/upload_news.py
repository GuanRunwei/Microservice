import requests
from requests import RequestException
from bs4 import BeautifulSoup
import json
import datetime
import time
import pymssql


headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'finance.eastmoney.com',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
           }

conn = pymssql.connect("0.0.0.0:1433", "sa", "Grw19980628", "AIStock")


def datetrans(text):
    dates = time.strptime(text, "%Y年%m月%d日 %H:%M")
    return time.strftime("%Y-%m-%d %H:%M", dates)


def get_urls(url: str) -> set:
    try:
        html = requests.get(url, headers)
        if html.status_code is 200:
            html_content = BeautifulSoup(html.text.encode("ISO-8859-1").decode("utf8"), "lxml")
            a_items = html_content.find("ul", id="newsListContent").find_all("a")
            result = set()
            for i in a_items:
                link = i.get("href")
                result.add(link)
        else:
            return None
    except RequestException:
        return None
    return result


def get_response(url: str):
    try:
        html = requests.get(url, headers)
        if html.status_code is 200:
            html_content = BeautifulSoup(html.text.encode("ISO-8859-1").decode("UTF-8"), "lxml")
            news_content = html_content.find("div", attrs={"class": "newsContent"})
        else:
            return None
    except RequestException:
        return None
    return news_content


def get_article():
    try:
        urls, result = get_urls("http://finance.eastmoney.com/news/cgnjj.html"), []
        for url in urls:
            news_content, count = get_response(url), 0
            title = news_content.find("h1").text
            issue_time = news_content.find("div", attrs=("class", "time"))
            source = news_content.find("div", attrs={"class", "source data-source"})
            entire_p = ""
            p_items = news_content.find_all("p")
            for p in p_items:
                if count is 0:
                    count += 1
                    continue
                entire_p += p.text + "\n"
                entire_p = entire_p.replace(" ", "").replace("\u3000", " ")
            if str(datetrans(issue_time.text)[0:10]).strip() == str(datetime.datetime.now().date()):
                result.append({"title": title, "paragraph": entire_p, "issue_time": datetrans(issue_time.text),
                               "source": source.get("data-source")})
                print({"title": title, "paragraph": entire_p, "issue_time": datetrans(issue_time.text),
                       "source": source.get("data-source")})
                if conn:
                    # print("连接成功！")
                    cursor = conn.cursor()
                    values = "('" + str(title) + "', '" + str(entire_p) + "', '" + str(
                        datetrans(issue_time.text)) + "', '" + str(source.get("data-source")) + "', '" + str(1) + "')"
                    sql_string = "insert into News (Title, Content, IssueTime, Source, NewsType) values %s" % values
                    print(sql_string)
                    cursor.execute(sql_string)
                    conn.commit()

    except Exception:
        return
