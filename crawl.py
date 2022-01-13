import urllib
from urllib.request import urlopen

from flask import Flask, render_template
import certifi
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

app = Flask(__name__)


ca = certifi.where()
# client = MongoClient('mongodb+srv://test:sparta@cluster0.p2cn0.mongodb.net/Cluster0?retryWrites=true&w=majority')
client = MongoClient('mongodb+srv://test:sparta@cluster0.rtjyu.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

# url title content hashtag를 크롤링 해온다. 없는 게시물은 보여주지 않음.

# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------
# --------------------------------------------------------------------

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


# 네이버 검색창에 검색하고 싶은 것을 검색후 url을 입력하여 할당함.
@app.route("/search", methods=['GET'])
def crawling():
    search_url = urllib.request.Request(url='search_give')
    print(search_url)
    with urllib.request.urlopen(search_url) as response:
        the_page = response.read()

    data = requests.get(the_page, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    search = soup.select('#main_pack > section > div > div._list > panel-list > div > more-contents > div > ul > li')

    # url title content hashtag를 크롤링 해온다.
    for i in search:
        url = i.select_one('div.total_wrap.api_ani_send > div > a')
        content = i.select_one('div.total_wrap.api_ani_send > div > div.total_group').text.strip()
        tag = i.select_one('div.total_tag_area')
        img = i.select_one('div.total_wrap.api_ani_send > a > span> img')

        if tag is None or tag.text is None:
            continue
        if img is None:
            continue

        url_list = url['href'], url.text, content, tag.text, img['src']

        lists = list(url_list)
        # print()
        return render_template('crawling.html', lists=lists)


# ---------------------------------------------------------------
# ---------------------------------------------------------------
# ---------------------------------------------------------------


# 일회용 컵 줄이기
# crawling(
#     'https://search.naver.com/search.naver?where=view&sm=tab_jum&query=%EC%9D%BC%ED%9A%8C%EC%9A%A9+%EC%BB%B5+%EC%A4%84%EC%9D%B4%EA%B8%B0')
#
# # 헌옷 재활용
# crawling(
#     'https://search.naver.com/search.naver?sm=tab_hty.top&where=view&query=%EC%9C%A0%EB%A6%AC%EB%B3%91+%EC%9E%AC%ED%99%9C%EC%9A%A9&oquery=%ED%97%8C%EC%98%B7+%EC%9E%AC%ED%99%9C%EC%9A%A9&tqi=hO%2BuJwp0Jy0ssi4OOhKssssssdV-261863&mode=normal')
#
# # 유리병 재활용
# crawling(
#     'https://search.naver.com/search.naver?sm=tab_hty.top&where=view&query=%EC%9C%A0%EB%A6%AC%EB%B3%91+%EC%9E%AC%ED%99%9C%EC%9A%A9&oquery=%ED%97%8C%EC%98%B7+%EC%9E%AC%ED%99%9C%EC%9A%A9&tqi=hO%2BuJwp0Jy0ssi4OOhKssssssdV-261863&mode=normal')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)