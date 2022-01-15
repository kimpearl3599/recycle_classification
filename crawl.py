import urllib
from urllib.request import urlopen

from bson import ObjectId
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import certifi
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

app = Flask(__name__)


client = MongoClient('mongodb+srv://test:sparta@cluster0.uvimx.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
# client = MongoClient('mongodb+srv://tmdgus5611:sparta@cluster0.rtjyu.mongodb.net/Cluster0?retryWrites=true&w=majority',
#                      tlsCAFile=ca)
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
    # search_url = urllib.request.urlopen('search_give')
    search_url = 'https://search.naver.com/search.naver?where=view&sm=tab_jum&query=%EC%9D%BC%ED%9A%8C%EC%9A%A9+%EC%BB%B5+%EC%A4%84%EC%9D%B4%EA%B8%B0'
    data = requests.get(search_url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    search = soup.select('#main_pack > section > div > div._list > panel-list > div > more-contents > div > ul > li')
    # print(search)
    # url title content hashtag를 크롤링 해온다.

    cup_lists = []
    for i in search:
        url = i.select_one('div.total_wrap.api_ani_send > div > a')
        content = i.select_one('div.total_wrap.api_ani_send > div > div.total_group').text.strip()
        tag = i.select_one('div.total_tag_area')
        img = i.select_one('div.total_wrap.api_ani_send > a > span> img')

        if tag is None or tag.text is None:
            continue
        if img is None:
            continue

        url_list = {'url': url['href'],
                    'title': url.text,
                    'content': content,
                    'tag': tag.text,
                    'img': img['src']}

        cup_lists.append(url_list)
        # print(lists)

    glasses_url = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=view&query=%EC%9C%A0%EB%A6%AC%EB%B3%91+%EC%9E%AC%ED%99%9C%EC%9A%A9&oquery=%ED%97%8C%EC%98%B7+%EC%9E%AC%ED%99%9C%EC%9A%A9&tqi=hO%2BuJwp0Jy0ssi4OOhKssssssdV-261863&mode=normal'

    glass_data = requests.get(glasses_url, headers=headers)

    glass_soup = BeautifulSoup(glass_data.text, 'html.parser')

    glasses_search = glass_soup.select(
        '#main_pack > section > div > div._list > panel-list > div > more-contents > div > ul > li')
    # print(search)
    # url title content hashtag를 크롤링 해온다.

    glass_lists = []
    for glass in glasses_search:
        url = glass.select_one('div.total_wrap.api_ani_send > div > a')
        content = glass.select_one('div.total_wrap.api_ani_send > div > div.total_group').text.strip()
        tag = glass.select_one('div.total_tag_area')
        img = glass.select_one('div.total_wrap.api_ani_send > a > span> img')

        if tag is None or tag.text is None:
            continue
        if img is None:
            continue

        glass_list = {'url': url['href'],
                      'title': url.text,
                      'content': content,
                      'tag': tag.text,
                      'img': img['src']}

        glass_lists.append(glass_list)
        # print(lists)

    upcycling_url = 'https://search.naver.com/search.naver?sm=tab_sug.top&where=view&query=%EC%97%85%EC%82%AC%EC%9D%B4%ED%81%B4%EB%A7%81&oquery=%EC%B9%9C%ED%99%98%EA%B2%BD%EC%A0%9C%ED%92%88&tqi=hPvSDsp0YiRssv7ITo4sssssst0-473338&acq=djqtk&acr=1&qdt=0&mode=normal'
    upcycle_data = requests.get(upcycling_url, headers=headers)

    upcycle_soup = BeautifulSoup(upcycle_data.text, 'html.parser')

    upcycling_search = upcycle_soup.select(
        '#main_pack > section > div > div._list > panel-list > div > more-contents > div > ul > li')
    # print(search)
    # url title content hashtag를 크롤링 해온다.

    upcycling_lists = []
    for upcycle in upcycling_search:
        url = upcycle.select_one('div.total_wrap.api_ani_send > div > a')
        content = upcycle.select_one('div.total_wrap.api_ani_send > div > div.total_group').text.strip()
        tag = upcycle.select_one('div.total_tag_area')
        img = upcycle.select_one('div.total_wrap.api_ani_send > a > span> img')

        if tag is None or tag.text is None:
            continue
        if img is None:
            continue

        upcycle_list = {'url': url['href'],
                        'title': url.text,
                        'content': content,
                        'tag': tag.text,
                        'img': img['src']}

        upcycling_lists.append(upcycle_list)

    clothes_url = 'https://search.naver.com/search.naver?where=view&sm=tab_jum&query=%ED%97%8C%EC%98%B7%EC%9E%AC%ED%99%9C%EC%9A%A9'
    clothes_data = requests.get(clothes_url, headers=headers)

    cloth_soup = BeautifulSoup(clothes_data.text, 'html.parser')

    clothes_search = cloth_soup.select(
        '#main_pack > section > div > div._list > panel-list > div > more-contents > div > ul > li')
    # print(search)
    # url title content hashtag를 크롤링 해온다.

    clothes_lists = []
    for cloth in clothes_search:
        url = cloth.select_one('div.total_wrap.api_ani_send > div > a')
        content = cloth.select_one('div.total_wrap.api_ani_send > div > div.total_group').text.strip()
        tag = cloth.select_one('div.total_tag_area')
        img = cloth.select_one('div.total_wrap.api_ani_send > a > span> img')

        if tag is None or tag.text is None:
            continue
        if img is None:
            continue

        clothes_list = {'url': url['href'],
                        'title': url.text,
                        'content': content,
                        'tag': tag.text,
                        'img': img['src']}

        clothes_lists.append(clothes_list)

    # print(lists)
    return render_template('crawling.html', cuplists=cup_lists, glasslists=glass_lists, upcyclelists=upcycling_lists,
                           clotheslists=clothes_lists)


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
