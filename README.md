# Word Trip : 서울 내 여행지 AI 추천 웹 애플리케이션
![image](https://user-images.githubusercontent.com/72599761/144171509-b8caf715-cd0b-449e-9e91-8feddcdaefc5.png)
#### 2021-10-15 ~ 2021-11-05

- 사용자가 입력한 키워드와 관련된 서울내 여행 명소를 1위부터 10위까지 추천해주는 AI 추천 Flask 기반 Web Appliation입니다.
- 구글 지도의 서울 25개구에 해당하는 여행지 리뷰 데이터를 기반으로 추천시스템을 통해 키워드와 관련된 서울 내 여행지 1위~10위까지 추천합니다. 
- 추천시스템은 키워드 기반 추천시스템, 명소 기반 추천 시스템 2가지 방식으로 나뉩니다. 
- 키워드 기반 추천 시스템은 사용자가 입력한 <b>감성 단어</b> 키워드와 유사한 단어를 Word2Vec모델에서 TF-IDF가중치를 구한 후, 코사인 유사도를 추출하여 추천합니다. 
- 키워드 기반 추천 시스템에서 감성 단어 키워드와 관련된 Word2Vec모델은 Plotly를 활용하여 Word2Vec 그래프로 시각화(Flask기반 Web Application)  
- 명소 기반 추천 시스템은 사용자가 입력한 <b>여행 명소</b> 키워드와 유사한 단어를 TF-IDF가중치를 구한 후, 코사인 유사도를 추출하여 추천합니다. 
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
<p>
1. 크롤링한 데이터 중에서 해당 구가 아닌 데이터 제거 <br> 
2. 결측값(NaN) 제거 <br> 
3. 중복값 제거 <br> 
4. 정규표현식을 사용하여 리뷰 정제 <br> 
5. Okt()를 이용하여 형태소를 분석 후 데이터 ‘명사’ ,’형용사’ 형태로 토큰화 <br> 
6. Stopwords를 이용하여 불용어 제거 <br> 
7. 명소와 명소에 해당하는 리뷰 단어 사전 만들기 <br>  </p>
<br><br>
### - 자연어 전처리 전
<br>

![image](https://user-images.githubusercontent.com/72599761/144172830-91c7c759-9877-4e17-9b81-428446d7abb2.png)

<br>
### - 자연어 전처리 후
<br>

![image](https://user-images.githubusercontent.com/72599761/144172860-865aad5b-8b29-4572-8faf-baae46e97caa.png)

<br><br><br>

## 3단계 : 코사인 유사도에 따른 추천 시스템 
<p> 코사인 유사도에 따른 추천시스템은 2가지 방식이 존재한다. <br>
첫번째는 단어(키워드) 기반 추천 시스템이고, 두번째는 명소 기반 추천 시스템이다. <br>
두가지 방식의 차이는 Word2Vec모델을 활용유무에 따라 나뉩니다. </p> 
<br><br>

![image](https://user-images.githubusercontent.com/72599761/144172900-aac4b35d-d2c2-4781-9fdb-3d345e857dcc.png)

<br>

### 1. 단어(키워드) 기반 추천 시스템 

### 2. 입력한 여행 명소 기반 추천 시스템 

<br><br><br>



## 4단계 : 웹 애플리케이션 (Flask)
<p>flask를 활용하여 Web Application을 구현하였습니다. </p>

<br><br>

### 1. 메인 화면

![main](https://user-images.githubusercontent.com/72599761/144175404-54e796f0-2dd6-4383-aed0-d09999afe852.png)

<br><br>

### 2. 감성 단어 기반 여행 명소 추천시스템

<br><br>

![word_1](https://user-images.githubusercontent.com/72599761/144175426-6f883505-2bfe-4585-bad1-067f036d702d.png)

<br><br>

![word_2](https://user-images.githubusercontent.com/72599761/144175437-44dac374-ad33-4a89-b8c9-c62353727d4c.png)

<br><br>

![word_3](https://user-images.githubusercontent.com/72599761/144175446-7143c09e-6ac1-4e97-b4bc-c9394114ff43.png)

<br><br>

![word_4](https://user-images.githubusercontent.com/72599761/144175469-ae1abd59-6ee5-4021-8fd6-a127324788d9.png)

<br><br>

### 3. 검색한 여행 명소와 유사한 여행 명소 추천 시스템

<br><br>

![attraction_1](https://user-images.githubusercontent.com/72599761/144175481-6b2ef1d0-fc5c-4c7c-b231-16a302cb1e30.png)

<br><br>

![attraction_2](https://user-images.githubusercontent.com/72599761/144175491-e6ecec26-329d-4922-83f3-88df4ef30103.png)

<br><br>


