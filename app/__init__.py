import cloudinary
from cloudinary import CloudUploader
# from mongo_connector import MongoConnector
from pymongo import MongoClient
import settings as ENV
from flask_cors import CORS
from flask import Flask, jsonify, request, render_template, redirect, url_for
from pil import Image
import pytesseract
import requests
import urllib
import cv2
import numpy as np
import json

# initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = ENV.SECRET_KEY

#open CORS
CORS(app)
# loop = asyncio.get_event_loop()
#initialize db
# db = MongoConnector()
mongo = MongoClient(ENV.MONGO_URI)
dbimg = mongo.ocr.images
dbdoc = mongo.ocr.insertdoc
dbres = mongo.ocr.pytesseract

#cloud config
cloudinary.config(
        cloud_name = ENV.CLOUDINARY_CLOUD_NAME,
        api_key = ENV.CLOUDINARY_API_KEY,
        api_secret = ENV.CLOUDINARY_API_SECRET
        )

#pytesseract ocr executable path
# pytesseract.pytesseract.tesseract_cmd = r'/app/.apt/usr/bin/tesseract'
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/share/tesseract-ocr/4.00/tessdata'
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

class Pytesseract():

    @staticmethod
    def check_json(request_json):
        content = request_json
        if 'image' in content:
            image = content.get('image')
        else:
            image = None
        if 'url' in content:
            url = content.get('url')
        else:
            url = None
        return image, url

    @classmethod
    def return_random_img(cls):
        test = dbres.aggregate([{'$sample': { 'size': 1 } }])
        for doc in test:
            return doc['char'], doc['word'], doc['secure_url']

    @classmethod
    def upload_image(cls, image64):
        image_id = str(datetime.now().timestamp()).replace('.', '')
        result = CloudUploader.upload(image64, public_id = "ocr/" + image_id)
        imgurl = result["secure_url"]
        img = cv2.imread(image64)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img, imgurl

    @classmethod
    def url_to_image(cls, image = None, url = None):
        if url != None and image = None:
            resp = urllib.request.urlopen(url)
            img = np.asarray(bytearray(resp.read()),dtype="uint8")
            img = cv2.imdecode(image, cv2.IMREAD_COLOR)
            return img, url
        elif image != None and url = None:
            img, url = cls.upload_image(image)
            return img, url
        
    
    @classmethod
    def get_bb_word(cls, image):
        try:
            hImg, wImg, _ = image.shape
            extract = pytesseract.image_to_data(image, lang = 'tha')
            tot = []
            for x, b in enumerate(extract.splitlines()):
                if x != 0:
                    b = b.split()
                    if len(b) == 12:
                        let, x, y, w, h = str(b[-1]), int(b[6]), int(b[7]), int(b[8]), int(b[9])
                        tot.append({'let' : let, 'x' : x, 'y': y, 'w' : w, 'h': h})
            return tot
        except Exception as e:
            print('word Exception', e)
            return jsonify({'message' : 'error')}, 403
    
                           
    @classmethod
    def insert_doc(cls, request_json):
        word = request_json['word']
        secure_url = request_json['url']
        userid = request_json['userid']
        pic_url = list(dbres.find({'secure_url' : secure_url}))
        pic_char = []
        in_char = []
        temp = []
        word_char = list(word)
        for i in range(len(pic_url[0]['char'])):
            pic_char.append(
                    pic_url[0]['char'][i]
                    )
        for i in range(len(word_char)):
            if word_char[i] == ' ':
                pass
            else:
                in_char.append(
                        word_char[i]
                        )
        temp.append({
            'userid' : userid,
            'secure_url' : secure_url,
            'char' : in_char,
            'pic_char' : pic_char
            })
        dbdoc.insert({
            'userid' : userid,
            'secure_url' : secure_url,
            'char' : in_char,
            'pic_char' : pic_char
            })
        return {'result' : temp, 'status' : 200}

@app.route('/')
def hello():
    return 'Hello world!'

@app.route('/image', methods = ['GET', 'POST'])
def index():
    try:
        if request.method == 'GET':
            image, url = Pytesseract.url_to_image(Pytesseract.check_json(request.get_json()))
            char = Pytesseract.get_bb_char(image)
            word = Pytesseract.get_bb_word(image)
            return jsonify({
                'image' : image,
                'char' : char,
                'word' : word,
                'secure_url' : url,
                'status' : 200}), 200
        else:
            return jsonify({"message" : "Unknown error.", "status" : 401}) , 401
    except Exception as e:
        print(e)
        return json.dumps({'success' : True}), 200, {'ContentType' : 'application/json'}

@app.route("/ocr_save_text", methods = ['POST'])
def save_text():
    return jsonify(Pytesseract.insert_doc(request.get_json()))

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 80, debug = True)
