import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, session
import ssl
from datetime import datetime
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf
import codecs
import numpy as np
import base64
from PIL import Image
from io import BytesIO
import cv2
from io import BytesIO
from PIL import Image

# 학습시킨 binary classification model 불러오기 (출력층을 sigmoid 로 설정했기에, predict 하면 아웃풋이 0~1 로 나옴)
model = tf.keras.models.load_model('static/model/recycle.h5')
# 해당 모델은 아웃풋이 0이면 고양이, 1이면 강아지라고 판별한 것
# 아웃풋이 어떤지는 모델 생성 시 출력층을 어떻게 구성했는지에 따라 얼마든지 달라질 수 있음에 유의
# 모델 생성 시 출력층을 softmax 로 설정했다면 카테고리 갯수만큼 아웃풋이 나올 것
# 모델 생성 시 출력층을 sigmoid 로 설정했다면 0~1로 아웃풋이 나올 것

app = Flask(__name__)
# def decode_base64_url(url):
#     assert url.startswith('data:image/')
#     assert ';base64,' in url
#     schema, payload = url.split(',', 1)
#     # Maybe parse the schema if you want to know the image's type
#     # type = schema.split('/', 1)[-1].split(';', 1)[0]
#     return base64.urlsafe_b64decode(payload)
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
    return jsonify({'result':'success'})


@app.route('/result')
def result():
	  # 모델은 불러와져 있으니, 사용자가 올린 데이터를 predict 함수에 넣어주면 됨
		# 이미지이기에, rescale 및 size 조정을 위해 ImageDataGenerator 활용
    test_datagen = ImageDataGenerator(rescale = 1./255)
    test_dir = 'static/img'
    test_generator = test_datagen.flow_from_directory(
            test_dir,
            # target_size 는 학습할때 설정했던 사이즈와 일치해야 함
            target_size =(224, 224),
            color_mode ="rgb",
            shuffle = False,
            # test 셋의 경우, 굳이 클래스가 필요하지 않음
            # 학습할때는 꼭 binary 혹은 categorical 로 설정해줘야 함에 유의
            class_mode = None,
            batch_size = 12)
    pred = model.predict(test_generator)

    # 마지막으로 업로드한 사진에 대한 판별결과를 보여줌
    # 이 부분은 어떤 서비스를 만들고자 하는지에 따라서 얼마든지 달라질 수 있음
    categories = {'배터리':0, '음식물쓰레기':1, '갈색병':2, '박스':3, '의류':4,
            '초록병':5, '금속': 6, '종이':7, '플라스틱':8, '신발':9, '일반쓰레기':10,
            '유리':11
            }

    for key, value in categories.items():
        if value == np.argmax(pred[-1]):
            result = key

    return render_template('ml_result.html', resultt = result)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug = True)



    # if np.argmax(pred[-1]) == 0:
    #     result = '배터리'
    #
    # elif np.argmax(pred[-1]) == 1:
    #     result = '음식물쓰레기'
    #
    # elif np.argmax(pred[-1]) == 2:
    #     result = '갈색병'
    #
    # elif np.argmax(pred[-1]) == 3:
    #     result = '박스'
    #
    # elif np.argmax(pred[-1]) == 4:
    #     result = '옷'
    #
    # elif np.argmax(pred[-1]) == 5:
    #     result = '초록병'
    #
    # elif np.argmax(pred[-1]) == 6:
    #     result = '금속'
    #
    # elif np.argmax(pred[-1]) == 7:
    #     result = '종이'
    #
    # elif np.argmax(pred[-1]) == 8:
    #     result = '플라스틱'
    #
    # elif np.argmax(pred[-1]) == 9:
    #     result = '신발'
    #
    # elif np.argmax(pred[-1]) == 10:
    #     result = '일반쓰레기'
    #
    # elif np.argmax(pred[-1]) == 11:
    #     result = '흰병'