from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import cv2
import numpy as np
import datetime

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
record = False


while True:

    ret, frame = capture.read()
    cv2.imshow("VideoFrame", frame)

    now = datetime.datetime.now().strftime("%d_%H-%M-%S")
    key = cv2.waitKey(33)

    if key == 27:
        break
    elif key == 26:
        print("캡쳐")
        cv2.imwrite(r"./images/image" + str(now) + ".png", frame)

capture.release()
cv2.destroyAllWindows()
