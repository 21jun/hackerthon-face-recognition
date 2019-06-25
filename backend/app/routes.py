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
        db="flasksteam",
        user="root", 
        password="1qazxc"
    )
    return db

db = pymysql.connect(
    host="localhost",
    port=3307,
    db="flasksteam",
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


@app.route("/db/applist")
def getApplist():
    db = db_conn()
    cursor = db.cursor()
    response = {
        'success': False,
        'applist': [],
        'error': '',
    }
    # if isLogin():
    SQL = "SELECT * FROM `applist` limit 10"
    cursor.execute(SQL)
    response["applist"] = cursor.fetchall()
    response["success"] = True
    cursor.close()
    return json.dumps(response)

def json_default(value): 
    if isinstance(value, datetime.date): 
        return value.strftime('%Y-%m-%d') 
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
    im.show()
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
        INSERT INTO user 
    '''
    # img = image_to_blob(request.form['photo'])
    aaa = request.form['photo']
    aaa = aaa.split(',')
    
    img = image_to_blob(aaa[1])
    
    image = Image.frombytes('RGB', (640, 480), img, 'raw')
    image.show()

    # pic = get_as_base64(request.form['photo'])

    # cursor.execute(SQL.format(appid=appid))
    # response["player_count"] = cursor.fetchall()
    # response["success"] = True
    # cursor.close()
    # #print("re", response)
    # print(img)
    # response['list'] = img
    return json.dumps(response, default = json_default)

# text 넣으면 applist 정보들 반환
@app.route("/db/applist/<text>")
def searchApp(text):
    db = db_conn()
    cursor = db.cursor()
    response = {
        'success': False,
        'list': [],
        'error': ''
    }

    print(text)

    SQL ='''
    SELECT 
        *
    FROM
        (SELECT 
            *
        FROM
            `applist`
        WHERE
            name LIKE '%%{text}%%') T1
            INNER JOIN
        `appinfo` T2 ON T2.appid = T1.appid
    '''
    cursor.execute(SQL.format(text=text))
    response["list"] = cursor.fetchall()
    response["success"] = True
    cursor.close()
    #print(response)
    return json.dumps(response, default = json_default)

# tag 넣으면 해당 태그게임들 반환
@app.route("/db/searchTag/<text>")
def searchTagGame(text):
    db = db_conn()
    cursor = db.cursor()
    response = {
        'success': False,
        'list': [],
        'error': ''
    }
    SQL ='''
    SELECT 
        T1.appid, T1.name
    FROM
        `applist` T1
            JOIN
        (SELECT 
            appid, tag_name
        FROM
            `tags` A
        JOIN taglist B ON A.tagid = B.tagid
        WHERE
            tag_name = '{text}') T2 ON T1.appid = T2.appid
    '''
    cursor.execute(SQL.format(text=text))
    response["list"] = cursor.fetchall()
    response["success"] = True
    cursor.close()
    #print(response)
    return json.dumps(response, default = json_default)

# tag , 최소 동접자수 넣으면 게임 추천
@app.route("/db/recommand/<tag>/<tag2>/<tag3>/<min>")
def recommandGame(tag, tag2, tag3, min):
    db = db_conn()
    cursor = db.cursor()
    response = {
        'success': False,
        'list': [],
        'error': ''
    }
    SQL ='''
    SELECT DISTINCT
        T1.appid, name, max_player
    FROM
        (SELECT 
            appid, COUNT(*)
        FROM
            (SELECT 
            appid, A.tagid, B.tag_name
        FROM
            (SELECT DISTINCT
            tagid, appid
        FROM
            `tags`) A
        LEFT JOIN (SELECT 
            *
        FROM
            `taglist`
        WHERE
            tag_name = '{tag}' OR tag_name = '{tag2}'
                OR tag_name = '{tag3}') B ON A.tagid = B.tagid
        WHERE
            B.tagid IS NOT NULL) T
        GROUP BY appid
        HAVING COUNT(*) >= 3) T1
            LEFT JOIN
        applist T2 ON T1.appid = T2.appid
            LEFT JOIN
        (SELECT 
            appid, MAX(count) AS max_player
        FROM
            `player_count`
        GROUP BY appid) C2 ON T1.appid = C2.appid
    WHERE
        C2.max_player > {min}
    ORDER BY C2.max_player DESC
    '''
    cursor.execute(SQL.format(tag=tag, tag2 = tag2, tag3 =tag3, min = min))
    response["list"] = cursor.fetchall()
    response["success"] = True
    cursor.close()
    # print(response)
    return json.dumps(response, default = json_default)

# appid 넣으면 게임 이름 반환하는 쿼리
@app.route("/db/name/<appid>")
def getGameName(appid):
    db = db_conn()
    cursor = db.cursor()
    response = {
        'success': False,
        'name': '',
        'error': ''
    }
    SQL ='''
    select name from applist where appid = {appid}
    '''
    cursor.execute(SQL.format(appid=appid))
    response["name"] = cursor.fetchall()
    response["success"] = True
    cursor.close()
    #print(response)
    return json.dumps(response, default = json_default)

@app.route("/db/alltag")
def getAlltags():
    db = db_conn()
    cursor = db.cursor()
    response = {
        'success': False,
        'list': '',
        'error': ''
    }
    SQL ='''
    select tag_name from taglist
    '''
    cursor.execute(SQL)
    response["list"] = cursor.fetchall()
    response["success"] = True
    cursor.close()
    #print(response)
    return json.dumps(response, default = json_default)

# appid 넣으면 게임 개발사, 퍼블리셔, 발매일 반환하는 쿼리
@app.route("/db/info/<appid>")
def getGameInfo(appid):
    db = db_conn()
    cursor = db.cursor()
    response = {
        'success': False,
        'info': '',
        'error': ''
    }
    SQL ='''
    select developer, publisher, DATE(release_date) from `appinfo` where appid = {appid}
    '''
    cursor.execute(SQL.format(appid=appid))
    response["info"] = cursor.fetchall()
    response["success"] = True
    cursor.close()
    #print(response)
    return json.dumps(response, default = json_default)

# appid 넣으면 게임 리뷰정보 반환
@app.route("/db/review/<appid>")
def getGameReviews(appid):
    db = db_conn()
    cursor = db.cursor()
    response = {
        'success': False,
        'list': [],
        'error': ''
    }
    SQL ='''
    SELECT 
        B.name, A.*
    FROM
        (SELECT 
            appid,
                MAX(recent_review_count),
                MAX(recent_review_possitive),
                MAX(all_review_count),
                MAX(all_review_possitive),
                DATE(date)
        FROM
            `app_review`
        GROUP BY appid , DATE(date)) A
            LEFT JOIN
        `applist` B ON A.appid = B.appid
    where A.appid = {appid}
    '''
    cursor.execute(SQL.format(appid=appid))
    response["list"] = cursor.fetchall()
    response["success"] = True
    cursor.close()
    #print(response)

    return json.dumps(response, default = json_default)

'''
set @prev = (select count from flasksteam.player_count where appid = 39120 limit 1);
SELECT
    appid, date, count,
    @prev as '전일 이용자',
    (count - @prev) / @prev * 100 as '증감량',
    @prev := count
FROM
    (SELECT
        appid, count, DATE(date) AS date
    FROM
        flasksteam.player_count
    WHERE
        appid = 39120
    GROUP BY appid , DATE(date)) A
'''

if __name__ == "__main__":
    # app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.debug = True
    app.run()
