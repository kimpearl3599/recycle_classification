import certifi
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient('mongodb+srv://test:sparta@cluster0.uvimx.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db = client.reviews


@app.route('/')
def home():
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
    #ObjectId 값을 html 함수의 인자로 받아서 ajax를 통해 'id_give'로 전달받음
    id = request.form['id_give']
    editComment = request.form['editComment_give']
    confirmPassword = request.form['confirmPassword_give']

    print(id)
    print(confirmPassword)
    print(editComment)

    #'id_give'로 받아온 id와 일치하는 '_id' 찾기
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





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
