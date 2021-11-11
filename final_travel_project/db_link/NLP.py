import pandas as pd
import numpy as np
import sys
import re
import csv
import sqlite3

from konlpy.tag import Okt
from konlpy.tag import Kkma

csv.field_size_limit(100000000) #csv 필드 사이즈 증가

# DB작업
# db에 연결
connection = sqlite3.connect('word_trip_final.db')

# Creating a cursor object to execute
# SQL queries on a database table
cursor = connection.cursor()

file_name = ['성북구','강동구']

for name in file_name:
    # 구글맵리뷰
    googlemap = pd.read_csv(f"{name}_ver2.csv", sep=',',
                            names=['구이름', '명소이름', '별점', '링크', '주소', '리뷰별점', '리뷰']) #이미지링크

    googlemap_ = googlemap.loc[:, ['구이름', '명소이름','주소', '리뷰']]

    # 해당 구가 아닌 데이터 제거해주기
    for i in range(len(googlemap_)):
        if f'{name}' not in googlemap_['주소'][i]:
            googlemap_ = googlemap_.drop(index=i, axis=0)
    
    # 새로 인덱싱
    googlemap_ = googlemap_.reset_index(drop=True)  # 인덱싱

    # 스탑워즈 불러오기
    df = pd.read_csv("stopwords_review.txt")
    stopwords = df.iloc[:, 0].unique()

    # 형태소 분석
    okt = Okt()

    # word열 추가
    googlemap_['word'] = 0
    try:
        for i in range(0, len(googlemap_)):

            # 리뷰
            googlemapwords = googlemap_['리뷰'][i]

            # 리뷰 정제
            letters_only = re.sub('[^0-9가-힣\s\.\!\?]*', '', googlemapwords)

            # 형태소 테이블
            sampledf = pd.DataFrame(okt.pos(letters_only, norm=True, stem=True))

            # 인덱싱
            googlemap_ = googlemap_.reset_index(drop=True)

            # 명사, 형용사, 동사만 추출하기
            try:
                sampledf = sampledf[(sampledf[1] == 'Noun') | (sampledf[1] == 'Adjective')]  # 2글자 이상인 단어만 가져와서 리스트 만들기
                spword = []

                for word in sampledf[0]:
                    if len(word) >= 2:
                        # 스탑워즈 제외하고 출력하기
                        if word not in (stopwords):
                            spword.append(word)

                # 장소별로 정제된 단어들을 리스트화해서 장소리뷰 테이블의 word컬럼에 담기
                a = pd.DataFrame(spword)[0].unique()
                googlemap_['word'][i] = a
            except KeyError:
                googlemap_['word'][i] = ""
    except KeyError:
        print('키에러')

    googlemap_.to_csv(f"{name}_전처리_1.csv")
    googlemap = pd.read_csv(f"{name}_전처리_1.csv")

    # 데이터 전처리
    googlemap = googlemap.reset_index(drop=True)  # 인덱싱
    googlemap['리뷰'] = googlemap.리뷰.str.replace('[^0-9|가-핳| ]', '')  # 정규표현식을 이용한 불용어 제거
    googlemap = googlemap.dropna(how='any')  # 중복제거

    googlemap = googlemap.reset_index(drop=True)  # 인덱싱
    googlemap_place = googlemap.loc[:, ['구이름','명소이름']]
    googlemap_place = googlemap_place.drop_duplicates(subset=None,
                                                      keep='first',
                                                      inplace=False,
                                                      ignore_index=True)  # 중복제거 명소이름, word만 저장

    googlemap_place.fillna({'명소이름': '없음'}, inplace=True)  # null값 없음으로 대체
    googlemap_place['word'] = ''  # word컬럼 추가, 데이터는 빈공백으로(문자)

    # googlemap_place 장소에 단어 집합 넣기
    for i in range(0, len(googlemap_place)):
        words = []
        for j in range(0, len(googlemap)):
            if googlemap_place['명소이름'][i] == googlemap['명소이름'][j]:
                words.append(googlemap['word'][j])

        googlemap_place['word'][i] = words

    # 특수문자 [,],등 리스트 불용어 제거
    for i in range(len(googlemap_place)):
        googlemap_place.word[i] = str(googlemap_place.word[i])

    for e in range(len(googlemap_place)):
        googlemap_place['word'][e] = googlemap_place.word[e].replace('[', '').replace(']', '').replace("'", '').replace('"','').replace(",", '').replace("\n", '')

    googlemap_place = googlemap_place.loc[:, ['구이름', '명소이름', 'word']]
    googlemap_place.to_csv(f'{name}_전처리2.csv')

    # csv파일 오픈
    file = open(f'{name}_전처리2.csv',encoding='UTF8')

    # Reading the contents of the
    # 구별 csv file
    reader = csv.reader(file)
    
    # csv 파일 헤더 제거
    header = next(reader)
    
    #  내용만 넣어놓음
    # csv file 내용 읽기
    contents = reader

    # 리뷰테이블에 insert할 쿼리문
    insert_records = "INSERT INTO review_nlp (id, gu_name, place_name, word) VALUES(?, ?, ?, ?)"

    # 리뷰테이블에 파일의 내용을 임포트
    cursor.executemany(insert_records, contents)

    # 전체 받아옴
    select_all = "SELECT * FROM review_nlp"
    rows = cursor.execute(select_all).fetchall()

    # 콘솔에 출력
    for r in rows:
        print(r)

    # 커밋
    connection.commit()

# 디비 연결 종료
connection.close()