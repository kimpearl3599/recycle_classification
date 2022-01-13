from flask import Flask, render_template, Response
import cv2
import datetime

app = Flask(__name__)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


def gen_frames():
    while True:

        success, frame = camera.read()  # read the camera frame

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()


            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            # now = datetime.datetime.now().strftime("%d_%H-%M-%S")
            # key = cv2.waitKey(33)

            # if key == 27:
            #     break
            # elif key == 26:
            #     print("캡쳐")

@app.route('/api/screenshot1')
def gen_frames_screenshot():
    success, frame = camera.read()  # read the camera frame


    if not success:
        break
    else:
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    now = datetime.datetime.now().strftime("%d_%H-%M-%S")
    cv2.imwrite(r"./images/image" + str(now) + ".png", frame)



@app.route('/')
def index():
    return render_template('index_test.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')






if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)