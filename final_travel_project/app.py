from flask import Flask, request, render_template, redirect, session
import route_update.word_route as wr
import route_update.attraction_route as ar
from flask import flash

import models as mo

import config

from models import db, migrate

#플라스크 객체 생성
app = Flask(__name__)

#시크릿 키 생성
app.secret_key = 'asfaf'

#플라스크 컨피그에 사용자정의 컨피그 추가
app.config.from_object(config)

#블루 프린트 등록
app.register_blueprint(wr.bp)
app.register_blueprint(ar.bp)

# ORM 연동
db.init_app(app)
migrate.init_app(app, db)

@app.route('/')
def root():
    return render_template('index.html')

# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('index.html')
#
# @app.errorhandler(500)
# def page_not_found2(error):
#     flash("검색한 값이 존재하지 않습니다.")
#     return render_template('index.html')

if __name__ == '__main__':
    app.run()#flask 서버 실행