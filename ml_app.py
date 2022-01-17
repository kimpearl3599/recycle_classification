import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import certifi
from pymongo import MongoClient

from bson.objectid import ObjectId
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf
import numpy as np

import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
# 학습시킨 binary classification model 불러오기 (출력층을 sigmoid 로 설정했기에, predict 하면 아웃풋이 0~1 로 나옴)
model = tf.keras.models.load_model('static/model/recycle.h5')
client = MongoClient('mongodb+srv://test:sparta@cluster0.uvimx.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db = client.reviews

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('take_a_picture.html')


# 이전에 드렸던 파일 업로드 자료의 함수와 거의 동일합니다.
@app.route('/fileupload', methods=['POST'])
def file_upload():
    file = request.files['file_give']
    # 해당 파일에서 확장자명만 추출
    extension = file.filename.split('.')[-1]
    # 파일 이름이 중복되면 안되므로, 지금 시간을 해당 파일 이름으로 만들어서 중복이 되지 않게 함!
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'{mytime}'
    # 파일 저장 경로 설정 (파일은 서버 컴퓨터 자체에 저장됨)
    save_to = f'static/img/object/{filename}.{extension}'
    # 파일 저장!
    file.save(save_to)
    # 해당 이미지의 데이터를 jinja 형식으로 사용하기 위해 넘김
    return jsonify({'result': 'success'})


@app.route('/result')
def result():
    # 모델은 불러와져 있으니, 사용자가 올린 데이터를 predict 함수에 넣어주면 됨
    # 이미지이기에, rescale 및 size 조정을 위해 ImageDataGenerator 활용
    path = "./static/img/object"
    file_list = os.listdir(path)
    picpic = file_list[-1]
    test_datagen = ImageDataGenerator(rescale=1. / 255)
    test_dir = 'static/img/'
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        # target_size 는 학습할때 설정했던 사이즈와 일치해야 함
        target_size=(224, 224),
        color_mode="rgb",
        shuffle=False,
        # test 셋의 경우, 굳이 클래스가 필요하지 않음
        # 학습할때는 꼭 binary 혹은 categorical 로 설정해줘야 함에 유의
        class_mode=None,
        batch_size=12)
    pred = model.predict(test_generator)
    print(test_datagen)
    # 마지막으로 업로드한 사진에 대한 판별결과를 보여줌
    # 이 부분은 어떤 서비스를 만들고자 하는지에 따라서 얼마든지 달라질 수 있음
    categories = {'배터리': 0, '음식물쓰레기': 1, '갈색병': 2, '박스': 3, '의류': 4,
                  '초록병': 5, '금속': 6, '종이': 7, '플라스틱': 8, '신발': 9, '일반쓰레기': 10,
                  '유리': 11
                  }

    for key, value in categories.items():
        if value == np.argmax(pred[-1]):
            result = key

    return render_template('ml_result.html', resultt=result, picpic=picpic)


##################################코멘트##############################

@app.route('/review')
def comment():
    return render_template('review.html')


# review 저장하기
@app.route('/api/review', methods=['POST'])
def save_review():
    nickname_receive = request.form['nickname_give']
    comment_receive = request.form['comment_give']
    password_receive = request.form['password_give']

    # 닉네임 코멘트 비밀번호 중 하나라도 입력하지 않을시에 작성하지 못하게 해야함
    doc = {
        'nickname': nickname_receive,
        'comment': comment_receive,
        'password': password_receive
    }
    db.reviews.insert_one(doc)

    return jsonify({'msg': '후기가 등록완료되었습니다.'})


# review 보여주기
@app.route('/api/review', methods=['GET'])
def show_review():
    # review 전체 불러오기
    data = list(db.reviews.find({}))

    # resData라는 빈리스트 생성하여 값을 집어넣는 방식
    resData = []
    for d in data:
        # ObjectId를 idx로 정의
        idx = d['_id']
        nickname = d['nickname']
        comment = d['comment']
        password = d['password']

        # key:value 형태로 만들어 빈리스트에 넣어줌
        # ObjectId는 문자형태로 바꾸어줌
        dset = {
            'id': str(idx),
            'nickname': nickname,
            'comment': comment,
            'password': password,
        }
        resData.append(dset)

    count_resdata = len(resData)
    return jsonify({'all_reviews': resData, 'all_count': count_resdata})


# review 수정하기
@app.route('/api/update', methods=['POST'])
def review_update():
    # ObjectId 값을 html 함수의 인자로 받아서 ajax를 통해 'id_give'로 전달받음
    id = request.form['id_give']
    editComment = request.form['editComment_give']
    confirmPassword = request.form['confirmPassword_give']

    print(id)
    print(confirmPassword)
    print(editComment)

    # 'id_give'로 받아온 id와 일치하는 '_id' 찾기
    data = db.reviews.find_one({'_id': ObjectId(id)})
    # 기존의 비밀번호 불러오기
    originPassword = data['password']

    print(data)

    # 기존의 비밀번호와 입력한 비밀번호 비교
    if originPassword != confirmPassword:
        return jsonify({'msg': '비밀번호가 일치하지 않습니다. 다시 입력해주세요!'})
    else:
        db.reviews.update_one({'_id': ObjectId(id)}, {'$set': {'comment': editComment}})
        return jsonify({'msg': '수정되었습니다.'})


# review 삭제하기
@app.route('/api/delete', methods=['POST'])
def review_delete():
    print("삭제진입")
    id = request.form['id_give']
    confirmPassword = request.form['confirmPassword_give']

    print(id)
    print(confirmPassword)

    data = db.reviews.find_one({'_id': ObjectId(id)})
    originPassword = data['password']

    print(data)
    print(originPassword)

    if originPassword != confirmPassword:
        return jsonify({'msg': '비밀번호가 일치하지 않습니다. 다시 입력해주세요!'})
    else:
        db.reviews.delete_one({'_id': ObjectId(id)})
        return jsonify({'msg': '삭제되었습니다.'})


###############################################################################
###########################################################승현님 크롤링 부분 ##########

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


###############################################################################################
###카테고리
@app.route('/category')
def category1():
    return render_template('recycle_classification.html')


###################################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
