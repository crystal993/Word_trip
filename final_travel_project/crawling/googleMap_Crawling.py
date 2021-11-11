import datetime
import requests
import csv
import time
import pandas as pd
import numpy as np
import cx_Oracle as orcCon
import pandas as pd

from typing import Container
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cx_Oracle import DatabaseError

# 크롤링을 할 지역명 입력
region = '성북구'

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36')

browser = webdriver.Chrome(options=options)

search_page = "https://www.google.com/maps/search/" + region + "명소"

browser.get(search_page)

res = requests.get(search_page)

while True :
    # 명소 페이지 이동 후 로딩을 위한 대기시간 추가
    time.sleep(5)

    # 명소는 한페이지당 최대 20개씩 표시
    #   -> 명소는 CSS Selector가 동일하지만 중간 div가 div[1], div[3], div[5] ... div[39]까지 홀수만을 가지므로 아래와 같이 For문 구성
    for i in range(1, 40, 2):
        time.sleep(5)
        # 명소 객체 검색
        scroll = browser.find_element(by=By.XPATH, value='//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]')

        # 명소 객체는 스크롤에 의해 동적으로 생성 -> 스크롤을 끝까지 내려야 한 페이지내의 모든 명소가 정상적으로 생성되므로
        # 처음으로 명소를 검색했을때 또는 명소 페이지를 이동했을때는 5초간 스크롤을 끝까지 내림
        start = datetime.datetime.now()
        end = start + datetime.timedelta(seconds=5)
        while True :
            browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scroll)
            time.sleep(1)

            if datetime.datetime.now() > end :
                break

        time.sleep(5)

        try :
            # 해당 명소에 리뷰가 작성되어 있는지 확인하기 위해 리뷰 링크 존재 유무를 확인
            #   -> 확인 후 리뷰가 없는 명소면 CSV에 작성하지 않음
            siteTotalReview = browser.find_element(by=By.XPATH, value='//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[{0}]/div/div[2]/div[2]/div[1]/div/div/div/div[3]'.format(i))

            if siteTotalReview.text == '리뷰 없음' :
                continue

            elem_child = browser.find_element(by=By.XPATH, value='//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[{0}]/div/a'.format(i))
            elem_child.send_keys(Keys.ENTER)
            time.sleep(2)

            # 명소이름 획득
            siteName = browser.find_element(by=By.CSS_SELECTOR, value="h1.x3AX1-LfntMc-header-title-title.gm2-headline-5")
            if siteName is not None:
                nameText = siteName.text
            else:
                nameText = ''

            # 명소평점 획득
            try :
                siteScore = browser.find_element(by=By.CSS_SELECTOR, value="span.aMPvhf-fI6EEc-KVuj8d")
                scoreText = siteScore.text
            except :
                scoreText = ''

            # 명소주소 획득
            siteAddr = browser.find_element(by=By.CSS_SELECTOR, value="div.QSFF4-text.gm2-body-2")
            if siteAddr is not None:
                addressText = siteAddr.text
            else:
                addressText = ''

            # 명소 대표 사진 링크 획득
            sitePhoto = browser.find_element(by=By.XPATH, value='//*[@id="pane"]/div/div[1]/div/div/div[1]/div[1]/button/img')
            if sitePhoto is not None:
                photoSrc = sitePhoto.get_attribute("src")
            else:
                photoSrc = ''

            time.sleep(5)

            # 리뷰 버튼 클릭
            try :
                 reviewBtn = browser.find_element(by=By.XPATH, value='//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/span[1]/span/span/span[2]/span[1]/button').send_keys(Keys.ENTER)
            except NoSuchElementException:
                print('except NoSuchElementException')
                browser.find_element(by=By.CSS_SELECTOR, value="#omnibox-singlebox > div.Nm8HZ-Nh13jb-H9tDt.omnibox-active > div.nhb85d-zuz9Sc-haAclf > button").send_keys(Keys.ENTER)

            time.sleep(3)

            # 현재높이 저장
            prev_height = browser.execute_script(
                "return document.querySelectorAll('div.siAUzd-neVct.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc').scrollHeight")

            interval_page_pre = 0
            interval_page_af = 10

            while True:
                try:
                    # 스크롤내리기
                    scroll = browser.find_element(by=By.XPATH, value='//*[@id="pane"]/div/div[1]/div/div/div[2]')
                    time.sleep(4)
                    browser.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scroll)

                    # 내려온 스크롤 높이 저
                    curr_height = browser.execute_script(
                        'return document.querySelector("div.siAUzd-neVct.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc").scrollHeight')

                    interval_page_pre = interval_page_pre + 20
                    interval_page_af = interval_page_af + 20

                    # 스크롤 높이로 종료시키기
                    if curr_height == prev_height:
                        break
                    prev_height = curr_height

                except Exception as w:
                    print(w)
                    break

            # 리뷰 데이터셋 만들 리스트
            containers = []

            # 리뷰 집합
            reviews = browser.find_elements(by=By.CSS_SELECTOR, value='span.ODSEW-ShBeI-text')
            # 리뷰 스코어 추가
            reviewScores = browser.find_elements(by=By.CSS_SELECTOR, value='span.ODSEW-ShBeI-H1e3jb')

            time.sleep(5)

            for j, review in enumerate(reviews):
                container = []
                reviewText = review.text

                if len(reviewScores) != 0 :
                    reviewScore = reviewScores[j].get_attribute("aria-label")
                else :
                    reviewScore = '별표 0개'

                # 공백 리뷰 제거
                if reviewText :
                    print(reviewText)

                    # 지역구 추가
                    container.append(region)

                    # 장소 추가
                    container.append(nameText)

                    # 명소 평점
                    container.append(scoreText)

                    # 사진 링크
                    container.append(photoSrc)

                    # 명소 주소
                    container.append(addressText)

                    # 리뷰 평점
                    container.append(reviewScore)

                    # 엔터키 친 리뷰 리플레이스
                    reviewText = reviewText.replace('\n', '')
                    container.append(reviewText)

                    containers.append(container)
                else:
                    pass

            df = pd.DataFrame(data = containers)

            # csv 파일 생성
            f = open(f'{region}.csv', 'a', encoding="utf-8-sig", newline='')
            wr = csv.writer(f)
            final_result = []

            for q in range(len(containers)):
                final_result = containers[q]
                wr.writerow(final_result)

            f.close()

            time.sleep(5)
            try:
                time.sleep(5)

                browser.find_element(by=By.XPATH, value='//*[@id="pane"]/div/div[1]/div/div/div[1]/div/div/div[1]/span/button').send_keys(Keys.ENTER)

                time.sleep(8)

                browser.find_element(by=By.XPATH, value='//*[@id="omnibox-singlebox"]/div[1]/div[1]/button').send_keys(Keys.ENTER)
            except:
                time.sleep(8)
                browser.find_element(by=By.XPATH, value='//*[@id="pane"]/div/div[1]').send_keys(Keys.ENTER)

        except NoSuchElementException :
            print('Exception')
            break

    if i == 39 :
        time.sleep(5)
        clickNextBtn = browser.find_element(by=By.CSS_SELECTOR, value="#ppdPk-Ej1Yeb-LgbsSe-tJiF1e").send_keys(Keys.ENTER)
    else :
        break