import os
import io
import time
import numpy as np
import cv2
import dlib
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug import secure_filename
import json
app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'PNG', 'JPG'])
IMAGE_WIDTH = 640
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def fwhr(parts):
    height = parts[50].y - parts[21].y
    width = parts[16].x - parts[0].x
    fwhr = width/height
    return round(fwhr, 2)

def height_ratio(parts):
    top_height = parts[33].y - parts[21].y
    bottom_height = parts[8].y - parts[33].y
    height_ratio_value = "{} : {}".format(top_height,bottom_height)
    return height_ratio_value

def width_ratio(parts):
    left_face = parts[57].y - parts[33].y
    left_eye = parts[42].x - parts[27].x
    middle_face = parts[42].x - parts[39].x
    right_eye = parts[39].x - parts[36].x
    right_face =parts[36].x - parts[0].x
    width_ratio_value = "{} : {} : {} : {}".format(left_face, left_eye, middle_face, right_face)
    return width_ratio_value
    

def mouse_ratio(parts):
    top_mouse = parts[16].x - parts[45].x
    bottom_mouse = parts[8].y - parts[57].y
    mouse_ratio_value = "{} : {}".format(top_mouse, bottom_mouse)
    return mouse_ratio_value


@app.route('/')
def index():
    return 'Hello World!'

@app.route('/show-data', methods=['POST'])
def post_json():
    if request.method == 'POST':
        img_file = request.files['img_file']

        # BytesIOで読み込んでOpenCVで扱える型にする
        f = img_file.stream.read()
        bin_data = io.BytesIO(f)
        file_bytes = np.asarray(bytearray(bin_data.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img_file and allowed_file(img_file.filename):
            filename = secure_filename(img_file.filename)
        else:
            return "許可されていない拡張子です"

        dets = detector(frame[:, :, ::-1])
        if len(dets) > 0:
            parts = predictor(frame, dets[0]).parts()
            #fWHRの検出
            fwhr_value = fwhr(parts)
            # Height-Ratioの検出
            height_ratio_value = height_ratio(parts)
            # Width-Ratioの検出
            width_ratio_value = width_ratio(parts)
            # Mouse-Ratioの検出
            mouse_ratio_value = mouse_ratio(parts)

            ys = {}
            data = {}
            data["fWHR"] = fwhr_value
            data["height_ratio"] = height_ratio_value
            data["width-ratio"] = width_ratio_value
            data["mouse_ratio"] = mouse_ratio_value

            result_json = json.dumps(data, ensure_ascii=False, indent=4)
            return result_json

        



@app.route('/show-image', methods=['POST'])
def uploaded_file():
    return "TankYou!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
