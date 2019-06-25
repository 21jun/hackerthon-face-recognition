from flask import Flask, session, redirect, url_for, escape, request
from flask_cors import CORS
import pymysql
import json
import datetime
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup as bs
from PIL import Image
from io import BytesIO
import recog
import base64

app = Flask(__name__)
# CORS 설정
# /db/ , /api/ 로 시작하는 모든 요청에 대해서 허용
cors = CORS(app, resources={
  r"/db/*": {"origin": "*"},
  r"/api/*": {"origin": "*"},
})

def db_conn():
    db = pymysql.connect(
        host="localhost",
        port=3307,
        db="test",
        user="root", 
        password="1qazxc"
    )
    return db

db = pymysql.connect(
    host="localhost",
    port=3307,
    db="test",
    user="root", 
    password="1qazxc"
)

cursor = db.cursor()



@app.route("/")
def index():
    print(session)
    return "Hello, world!"


@app.route("/test")
def test():
    testData = {
        'firstAttribute': 1,
        'secondAttribute': 2
    }
    return json.dumps(testData)


def json_default(value): 
    if isinstance(value, datetime.datetime): 
        return value.strftime('%Y-%m-%d, %H:%M:%S') 
    raise TypeError('not JSON serializable')

# 날짜 정보를 입력하면 그날의 최고 동접자수를 기록한 게임 20개 반환
@app.route("/db/playerCount/<date>")
def getPlayerCount(date):
    db = db_conn()
    cursor = db.cursor()
    print(date)

    response = {
        'success': False,
        'player_count': [],
        'date' : '',
        'error': ''
    }

    SQL = '''
    SELECT 
        *
    FROM
        (SELECT 
            B.appid, B.name, A.max_player, A.date
        FROM
            (SELECT 
            appid, MAX(count) AS max_player, DATE(date) AS date
        FROM
            `player_count`
        WHERE
            date(date) = {date}
        GROUP BY appid , date) A
        LEFT JOIN applist B ON B.appid = A.appid) B
    ORDER BY max_player DESC
    LIMIT 20
    '''
    cursor.execute(SQL.format(date=date))
    response["player_count"] = cursor.fetchall()
    response["success"] = True
    cursor.close()
    # print(type(response["player_count"][0][3]))
    # a = json.dumps(response, default = json_default)
    # print("a =", a.d)
    # print(response["player_count"])
    return json.dumps(response, default = json_default)

# appid 넣으면 tag 정보들 반환
@app.route("/db/tags/<appid>")
def getTags(appid):
    db = db_conn()
    cursor = db.cursor()
    response = {
        'success': False,
        'tags': [],
        'error': ''
    }

    SQL = '''
    select T2.tag_name
    from (select A.appid, A.name, B.tagid
        from `applist` A
                join `tags` B ON A.appid = B.appid
        where A.appid = {appid}) T1
        left join `taglist` T2 ON T1.tagid = T2.tagid;
    '''
    cursor.execute(SQL.format(appid=appid))
    response["tags"] = cursor.fetchall()
    response["success"] = True
    cursor.close()
    #print(response)
    return json.dumps(response, default = json_default)


def image_to_blob(text) :
    test = BytesIO(base64.b64decode(text))
    im = Image.open(BytesIO(base64.b64decode(text)))
    # im.show()
    im = np.array(im)
    result = im.tobytes()
    return result

def get_as_base64(url):

    return base64.b64decode(url)


@app.route("/api/regist/", methods=["POST"])
def getRegistInfo():
    db = db_conn()

    cursor = db.cursor()
    response = {
        'success': False,
        'list': [],
        'error': ''
    }
    # print(request.form['photo'])
    SQL = '''
        INSERT INTO user2 (user_id, name, birth, phone, face_image, reg_date)
        VALUES (%s, %s, %s, %s, %s, now())
    '''
    base64txt = request.form['photo']
    base64txt = base64txt.split(',')

    user_id = int(request.form['user_id'])
    name = request.form['name']
    birth = request.form['birth']
    phone = request.form['phone']
    email = request.form['email']

    face_image = image_to_blob(base64txt[1])



    cursor.execute(SQL, (int(user_id), name, birth, phone, face_image))
    db.commit()

    # 이미지 출력
    image = Image.frombytes('RGB', (640, 480), face_image, 'raw')
    image.show()
    recog.isLoaded = False;
    
    return json.dumps(response, default = json_default)

@app.route("/api/detect/", methods=["POST"])
def getFrameToDetect():
    db = db_conn()

    cursor = db.cursor()
    response = {
        'success': False,
        'list': [],
        'img':[],
        'error': ''
    }

    base64txt = request.form['photo']
    base64txt = base64txt.split(',')
    face_image = image_to_blob(base64txt[1])

    # image = Image.frombytes('RGB', (640, 480), face_image, 'raw')
    # image.show()
    location = request.form['location']
    print(location)



    if recog.isLoaded:
        pass
    else:
        print("enrolling")
        imgs, names, ids = recog.get_img_from_db2()
        # print(len(imgs), len(names), "===========")
        # print(imgs[4])
        recog.enroll(imgs, names, ids)
        recog.isLoaded = True

    # img = recog.get_img_from_db(4)
    print("detecting")
    img = face_image
    # name_list, pil_image = recog.recognition(img)
    name_list, id_list = recog.realtime_recognition(img, location)


    response['list'] = name_list
    # response['img'] = pil_image.tobytes()
    return json.dumps(response, default = json_default)

@app.route("/api/log/<user_id>")
def getUserTimeSpend(user_id):

    response = {
        'success': False,
        'list': [],
        'error': ''
    }

    db = db_conn()
    cursor = db.cursor()
    SQL = '''
    SELECT location, date from visit_log where user_id = %s
    '''

    cursor.execute(SQL, (user_id))
    result = cursor.fetchall()


    # print(result)
    response["list"] = result
    response["success"] = True
    cursor.close()
    #print(response)
    return json.dumps(response, default = json_default)


if __name__ == "__main__":
    # app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.debug = True
    app.run()