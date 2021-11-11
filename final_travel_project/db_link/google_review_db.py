import pandas as pd
import sqlite3
import csv
from hanspell import spell_checker
import re

con = sqlite3.connect("word_trip_final.db") # 저장할 DB명 작성
cur = con.cursor()


# 기존테이블 존재하면 삭제
cur.execute("DROP TABLE IF EXISTS BASE")
cur.execute("DROP TABLE IF EXISTS ATTRACTION")
cur.execute("DROP TABLE IF EXISTS REVIEW")
cur.execute("DROP TABLE IF EXISTS REVIEW_TEXT")
cur.execute("DROP TABLE IF EXISTS TEMP")


# BASE테이블 생성
cur.execute("CREATE TABLE BASE (gu_name text(20), attr_name text(100),"
            " stars integer, pic_link text(1000), address text(500), review_stars text(20), review_text text(1000))")

area = ['마포구','서대문구','은평구','종로구','중구',
        '용산구','성동구','광진구','동대문구','성북구',
        '강북구','도봉구','노원구','중랑구','강동구',
        '송파구','강남구','서초구','관악구','동작구',
        '영등포구','금천구','구로구','양천구','강서구']

for i in range(len(area)):
    # CSV파일 테이블에 삽입
    file = open(f"../area/{area[i]}_ver2.csv", encoding='UTF-8')
    contents = csv.reader(file)
    # TEMP테이블 생성
    cur.execute("CREATE TABLE TEMP (gu_name text(20), attr_name text(100),"
                " stars integer, pic_link text(1000), address text(500), review_stars text(20), review_text text(1000))")
    insert_records = "INSERT INTO TEMP (gu_name, attr_name, stars, pic_link, address, review_stars, review_text) " \
                     "VALUES(?, ?, ?, ?, ?, ?, ?)"
    cur.executemany(insert_records, contents)

    # 해당 지역구 레코드만 남기기
    cur.execute(f"DELETE FROM TEMP WHERE address NOT LIKE '서울특별시 {area[i]}%'")

    # 해당 내용을 BASE테이블에 저장 후 TEMP테이블 삭제
    cur.execute("INSERT INTO BASE SELECT * FROM TEMP")
    cur.execute("DROP TABLE TEMP")

# 리뷰 테이블 생성 : REVIEW
cur.execute("CREATE TABLE REVIEW (idx integer primary key autoincrement, gu_name text(50), attr_name text(100),review_stars text(20), review_text text(1000))")
# BASE테이블에서 review테이블의 요소가져오기
cur.execute("INSERT INTO REVIEW (gu_name, attr_name, review_stars, review_text) SELECT gu_name, attr_name, review_stars, review_text FROM BASE")

# 관광명소 테이블 생성 : ATTRACTION
cur.execute("CREATE TABLE ATTRACTION (gu_name text(20), attr_name text(100),"
                " stars integer, pic_link text(1000), address text(500))")
#BASE테이블에서 ATTRACTION테이블 요소들 가져오기
cur.execute("INSERT INTO ATTRACTION (gu_name, attr_name, stars, pic_link, address) SELECT gu_name, attr_name, stars, pic_link, address FROM BASE")


# 관광명소 테이블 - 중복 레코드 삭제 : DataFrame으로 변환 후 중복 제거, 다시 sql로 저장
df = pd.read_sql("SELECT * FROM ATTRACTION", con, index_col=None)
df = df.drop_duplicates(['attr_name'], keep = 'first', ignore_index = True)
df.to_sql('ATTRACTION', con, if_exists='replace') # 이미 존재하는 테이블 이름일 때 replace:  기존 테이블을 삭제하고 새로 테이블을 생성한 후 데이터를 삽입


# 리뷰 테이블 - 명소 list만들기
df = pd.read_sql("SELECT * FROM REVIEW", con, index_col=None)
df_name = df.loc[:,'attr_name'] # 리뷰 전체 테이블에서 '명소'컬럼만 빼오기
df_name = df_name.drop_duplicates()
attr_name_list = df_name.values.tolist() # 명소 list만듦

cur.execute("CREATE TABLE IF NOT EXISTS REVIEW_SLIM (idx, gu_name, attr_name text(100),review_stars text(20), review_text text(1000))")

# 한 명소당 5개의 리뷰 출력
for j in range(len(attr_name_list)):
    cur.execute("INSERT INTO REVIEW_SLIM (idx, gu_name, attr_name, review_stars, review_text) "
                f"select idx, gu_name, attr_name, review_stars, review_text from REVIEW where attr_name='{attr_name_list[j]}' limit 5")

# review_slim 테이블명 review로 변경
cur.executescript("""
        DROP TABLE REVIEW;
        ALTER TABLE REVIEW_SLIM RENAME TO REVIEW;
    """)


#REVIEW테이블의 REVIEW_TEXT칼럼 맞춤법+ 띄어쓰기 검사
#!pip install git+https://github.com/haven-jeon/PyKoSpacing.git 설치 필요

review_text = pd.read_sql("SELECT review_text FROM REVIEW", con, index_col=None)
#print(len(review_text['review_text']))
for k in range(len(review_text['review_text'])):
    sent = review_text['review_text'][k]
    #특수문자 제거
    new_sent = sent.replace(" ", '') # 띄어쓰기가 없는 문장 임의로 만들기
    new_sent = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', new_sent)
    spelled_sent = spell_checker.check(new_sent)
    checked_sent = spelled_sent.checked
    review_text['review_text'][k] = checked_sent


#REVIEW_TEXT 테이블에 넣기
review_text.to_sql('REVIEW_TEXT', con, schema=review_text, if_exists='replace') # 이미 존재하는 테이블 이름일 때 replace:  기존 테이블을 삭제하고 새로 테이블을 생성한 후 데이터를 삽입

pd_review = pd.read_sql("SELECT * FROM REVIEW", con, index_col=None)
pd_review.rename(columns={'review_text':'review_text_be'},inplace = True)
pd_reviewtext = pd.read_sql("SELECT * FROM REVIEW_TEXT", con, index_col=None)
pd_reviewall = pd.concat([pd_review,pd_reviewtext],axis=1)
pd_review_final= pd_reviewall.drop([pd_reviewall.columns[0],pd_reviewall.columns[4],pd_reviewall.columns[5]],axis=1)
pd_review_final.to_sql('REVIEW', con, if_exists='replace')

cur.execute("DROP TABLE REVIEW_TEXT")

con.commit()
con.close()






