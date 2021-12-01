# Word Trip : 서울 내 여행지 AI 추천 웹 애플리케이션
![image](https://user-images.githubusercontent.com/72599761/144171509-b8caf715-cd0b-449e-9e91-8feddcdaefc5.png)
#### 2021-10-15 ~ 2021-11-05

- 사용자가 입력한 키워드와 관련된 서울내 여행 명소를 1위부터 10위까지 추천해주는 AI 추천 Flask 기반 Web Appliation입니다.
- 구글 지도의 서울 25개구에 해당하는 여행지 리뷰 데이터를 기반으로 사용자가 입력한 키워드와의 코사인유사도를 측정하여 여행지를 추천합니다.
- 사용자가 입력한 키워드와 유사한 단어를 Word2Vec모델에서 TF-IDF가중치를 구한 후, 코사인 유사도를 추출
<br><br><br>

![image](https://user-images.githubusercontent.com/72599761/144172604-e02bfda2-3fe0-4277-bbd0-5dc295de266f.png)
<br><br><br>

![image](https://user-images.githubusercontent.com/72599761/144172658-a366d237-7638-4cdf-ab5d-af87bd51b114.png)
 총 4단계의 시스템으로 구성되어 있다.
<br><br><br>

## 1단계 : 웹 크롤링 및 데이터 수집과 저장

![image](https://user-images.githubusercontent.com/72599761/144172682-aba6a7d8-c548-4db6-a1eb-9e37489d6a88.png)
<br><br><br>

## 2단계 : 자연어 전처리 (Pre-NLP)

![image](https://user-images.githubusercontent.com/72599761/144172830-91c7c759-9877-4e17-9b81-428446d7abb2.png)
![image](https://user-images.githubusercontent.com/72599761/144172840-35451ff6-19c7-43ab-81f5-7503c88dfeef.png)
![image](https://user-images.githubusercontent.com/72599761/144172860-865aad5b-8b29-4572-8faf-baae46e97caa.png)
<br><br><br>

## 3단계 : 코사인 유사도에 따른 추천 시스템 
<p> 코사인 유사도에 따른 추천시스템은 2가지 방식이 존재한다. <br>
첫번째는 단어(키워드) 기반 추천 시스템이고, 두번째는 명소 기반 추천 시스템이다. 
두가지 방식의 차이는 Word2Vec모델을 활용유무에 따라 나뉜다. </p> 

![image](https://user-images.githubusercontent.com/72599761/144172900-aac4b35d-d2c2-4781-9fdb-3d345e857dcc.png)
<br><br><br>

## 4단계 : 웹 애플리케이션 (Flask)


