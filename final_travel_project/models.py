import requests
from bs4 import BeautifulSoup

import urllib.request
import json
from pprint import pprint

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import session

import pandas as pd
import numpy as np
import sys
from konlpy.tag import Okt
from konlpy.tag import Kkma
import re

import pandas as pd
import numpy as np
import sys
from konlpy.tag import Okt
from konlpy.tag import Kkma
import re
import sqlite3
from gensim.models import Word2Vec

db = SQLAlchemy()
migrate = Migrate()

class Attraction(db.Model):#vo겸 테이블
    index = db.Column(db.Integer, primary_key=True)
    gu_name = db.Column(db.String, nullable=False) #autoincrement
    attr_name = db.Column(db.String, nullable=False)
    stars = db.Column(db.String, nullable=False)
    pic_link = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

class review(db.Model):#vo겸 테이블
    idx = db.Column(db.Integer, primary_key=True)
    gu_name = db.Column(db.String, nullable=False) #autoincrement
    attr_name = db.Column(db.String, nullable=False)
    review_stars = db.Column(db.String, nullable=False)
    review_text = db.Column(db.String, nullable=False)

class review_nlp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gu_name = db.Column(db.String(20), nullable=True)
    place_name = db.Column(db.String(20), nullable=True)
    word = db.Column(db.String(100000), nullable=False)

class review_nlp2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gu_name = db.Column(db.String(20), nullable=True)
    place_name = db.Column(db.String(20), nullable=True)
    word = db.Column(db.String(100000), nullable=False)

class place_recommend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gu_name = db.Column(db.String(20), nullable=True)
    place_name = db.Column(db.String(20), nullable=True)
    word = db.Column(db.String(100000), nullable=False)
    score = db.Column(db.Float, nullable=False)

class MapService:#비즈니스 로직. 외부에 제공할 기능구현
    def getCloseSiteList(self) :
        siteList = Attraction.query.all()

        return siteList

class ReviewService:
    def getAll(self):
        db.session.commit()
        return review_nlp.query.order_by(review_nlp.id.asc())

    def keword_similar(self, searchWord: str):
        import gensim
        from konlpy.tag import Okt
        # 추천 시스템 부분
        # Word2Vec 모델 불러오기
        okt = Okt()
        embedding_model = gensim.models.Word2Vec.load('Final_Word2Vec_ko.bin')

        keyword = searchWord  # 힐링 #자연 #운동 #공원 # ....
        keyword = okt.morphs(keyword, stem=True)  # 키워드의 원형을 찾아주는 옵션, 그래요 -> 그렇다
        FirstKeyword = keyword[0]

        # check embedding result
        VecWords = embedding_model.wv.most_similar(positive=[FirstKeyword], topn=100)
        Veclist1 = []  # 단어를 담을 리스트
        for i in range(0, 31):
            Veclist1.append(VecWords[i][0])

        myVec = Veclist1  # 단어 리스트

        return myVec

    def keyword_recommend(self, myWordList):

        try:
            queryset = review_nlp.query.order_by(review_nlp.id.asc())  # SQLAlchemy가 만들어준 쿼리, 하지만 .all()이 없어 실행되지는 않음
            df = pd.read_sql(queryset.statement, queryset.session.bind)

            # 데이터 프레임
            data_df = df

            train_data = data_df

            myplace = train_data

            # 키워드와 유사한 단어들 공백기준으로 한 문장으로 이어붙이기
            mysent = ""
            for i in myWordList:
                mysent += "".join(i)
                mysent += " "

            # 단어 사전을 만듬
            mydf1 = pd.Series(['구', '입력', mysent], index=['gu_name', 'place_name', 'word'])
            myplace = myplace.append(mydf1, ignore_index=True)
            myplace.iloc[-1, :]

            # TF-IDF구하기
            # Tfidf_matrix : 장소갯수 x 장소를 표현하는데 쓰인 단어 수
            from sklearn.feature_extraction.text import TfidfVectorizer
            Tfidf = TfidfVectorizer()
            Tfidf_matrix = Tfidf.fit_transform(myplace['word'])

            # 코사인유사도
            # Tfidf_matrix 기반으로 생성
            from sklearn.metrics.pairwise import linear_kernel
            cosine_sim = linear_kernel(Tfidf_matrix, Tfidf_matrix)

            # 코사인유사도
            simScores = list(enumerate(cosine_sim[-1]))

            # simScores : 튜플 (인덱스,코사인유사도)
            # score 순으로 정렬
            simScores = sorted(simScores, key=lambda x: x[1], reverse=True)

            # 코사인유사도 기준 내림차순 정렬된 튜플중 자기 제외(0번째인덱스)하고 300개 뽑음
            simScores = simScores[1:300]

            # 상위 300개 장소의 인덱스값 저장
            idx = [i[0] for i in simScores]
            RecPlacelist = myplace.iloc[idx]

            print(RecPlacelist[['gu_name', 'place_name', 'word']])

            self.deleteReview()

            for index, row in RecPlacelist.iterrows():
                gu_name = row['gu_name']
                place_name = row['place_name']
                word = row['word']

                self.addReview(review_nlp2(gu_name=gu_name, place_name=place_name, word=word))
        except KeyError:
            print('키에러')


        return RecPlacelist[['gu_name', 'place_name', 'word']]

    def place_recommend(self, place_name):

        try:
            queryset = review_nlp.query.order_by(review_nlp.id.asc())  # SQLAlchemy가 만들어준 쿼리, 하지만 .all()이 없어 실행되지는 않음
            place_df = pd.read_sql(queryset.statement, queryset.session.bind)

            place_df = place_df.loc[:, ['gu_name', 'place_name', 'word']]

            # 정규 표현식을 통한 한글 외 문자 제거
            place_df['word'] = place_df['word'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]", "")

            # tf-idf 행렬만들기
            # 장소갯수 x 이 장소를 표현하는데 필요한 단어의 갯수
            from sklearn.feature_extraction.text import TfidfVectorizer
            tfidf = TfidfVectorizer()
            Tfidf_matrix = tfidf.fit_transform(place_df.word)

            # 코사인유사도
            from sklearn.metrics.pairwise import linear_kernel
            cosine_sim = linear_kernel(Tfidf_matrix, Tfidf_matrix)

            # 장소 이름으로 인덱스 만들기
            indices = pd.Series(place_df.index, index=place_df['place_name']).drop_duplicates()

            # place_name 해당하는 인덱스 저장
            idx = indices[place_name]

            # 모든 장소에 대해서 place_name와의 유사도를 구하기
            sim_scores = list(enumerate(cosine_sim[idx]))

            # score 순으로 정렬 내림차순, 유사도가 높은 순서대로
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

            # 가장 유사한 100개의 장소를 받아옴
            sim_scores = sim_scores[1:300]

            # 인덱스 받아오기
            place_indices = [i[0] for i in sim_scores]

            # 기존에 읽어들인 데이터에서 해당 인덱스의 값을 가져오기 스코어 열을 추가
            result_df = place_df.iloc[place_indices].copy()
            result_df['score'] = [i[1] for i in sim_scores]

            self.deleteReview2()

            for index, row in result_df.iterrows():
                gu_name = row['gu_name']
                place_name = row['place_name']
                word = row['word']
                score = row['score']

                self.addReview2(place_recommend(gu_name=gu_name, place_name=place_name, word=word, score=score))

            return result_df

        except KeyError:
            print('키에러')

    def keywordScatterGraph(self, myWordList, searchWord):
        import gensim
        embedding_model = gensim.models.Word2Vec.load('Final_Word2Vec_ko.bin')
        myGraphVec = [embedding_model.wv[v] for v in myWordList]  # 그래프, 키워드와 유사한 단어 30개의 벡터들

        return myGraphVec

    def addReview(self, b: review_nlp2):
        db.session.add(b)
        db.session.commit()

    def addReview2(self, b: place_recommend):
        db.session.add(b)
        db.session.commit()

    def deleteReview(self):
        w = review_nlp2.query.count()
        for i in range(1, w + 1):
            q = review_nlp2.query.get(i)
            db.session.delete(q)
        db.session.commit()

    def deleteReview2(self):
        w = place_recommend.query.count()
        for i in range(1, w + 1):
            q = place_recommend.query.get(i)
            db.session.delete(q)
        db.session.commit()

    def mapReview(self, guname: str):
        db.session.commit()
        limit_num = 10
        nlp2 = review_nlp2.query.filter_by(gu_name=guname).limit(limit_num)
        # .order_by(review_nlp2.id.asc()) -> 이미 코사인유사도 비율 순으로 db에 저장되어 있어서
        # 아이디 순으로 정렬하면 정확도와 상관없이 나오게 됨.
        return nlp2

    def mapPlace(self, guname: str):
        db.session.commit()
        limit_num = 10
        place = place_recommend.query.filter_by(gu_name=guname).limit(limit_num)
        # .order_by(place_recommend.score.asc()) -> 이미 코사인유사도 비율 순으로 db에 저장되어 있어서
        # 아이디 순으로 정렬하면 정확도와 상관없이 나오게 됨.
        return place

    def getAttrByName(self, attr_name: str):  # attr_name 검색
        print('attr_name:', attr_name)
        return Attraction.query.filter(Attraction.attr_name == attr_name).all()  # filter():검색 조건 추가하는 함수

    def getAttrByReview(self, attr_name: str):  # attr_name 검색
        print('attr_name:', attr_name)
        return review.query.filter(review.attr_name == attr_name).all()  # filter():검색 조건 추가하는 함수