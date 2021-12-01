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


## - 선정 이유 

<p> 이전 프로젝트 '편행 : 편한 여행' 에서는 여행지를 검색했을 때 1박 2일 교통편, 숙박편만 추천해주는 시스템입니다. <br>
여행지에 관한 정보는 제공하지 않기 때문에 이를 보완하기 위해 여행지 추천 시스템을 제작하게 되었습니다. </p> <br>

![image](https://user-images.githubusercontent.com/72599761/144172604-e02bfda2-3fe0-4277-bbd0-5dc295de266f.png)
<br><br><br>

![image](https://user-images.githubusercontent.com/72599761/144172658-a366d237-7638-4cdf-ab5d-af87bd51b114.png)
 총 4단계의 시스템으로 구성되어 있습니다.
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
<p> 코사인 유사도에 따른 추천시스템은 2가지 방식이 존재합니다. <br>
첫번째는 단어(키워드) 기반 추천 시스템이고, 두번째는 명소 기반 추천 시스템입니다. <br>
두가지 방식의 차이는 Word2Vec모델을 활용유무에 따라 나뉩니다. </p> 
<br><br>

![image](https://user-images.githubusercontent.com/72599761/144172900-aac4b35d-d2c2-4781-9fdb-3d345e857dcc.png)

<br>

```python
gu_name=''
def getRecommendation(gu_name = gu_name):
    
    # TF-IDF
    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf = TfidfVectorizer()
    Tfidf_matrix = tfidf.fit_transform(place_df.word)

    # 코사인유사도 : TF-IDF가중치를 기반으로 생성
    from sklearn.metrics.pairwise import linear_kernel
    cosine_sim = linear_kernel(Tfidf_matrix, Tfidf_matrix)
    
    #코사인유사도
    simScores = list(enumerate(cosine_sim[-1])) 
    
    # simScores : 튜플 (인덱스,코사인유사도)
    simScores = sorted(simScores, key=lambda x: x[1] ,reverse=True) # score 순으로 정렬
    
    # 코사인유사도 기준 내림차순 정렬된 튜플중 자기 제외(0번째인덱스)하고 300개 뽑음
    simScores = simScores[1:300]
    
    # 상위 300개 장소의 인덱스값 저장
    idx = [i[0] for i in simScores]
    
    # 상위 300개 장소를 저장     
    RecPlacelist = train_data2.iloc[idx]
    
    # score 열에 코사인 유사도 값도 저장     
    RecPlacelist['score'] = [i[1] for i in simScores]
    
    # 해당 구 이름에 해당하는 여행지 10개 출력    
    return RecPlacelist[RecPlacelist['gu_name']==gu_name].head(10)

```


<br><br><br>



## 4단계 : 웹 애플리케이션 (Flask)
<p>flask를 활용하여 Web Application을 구현하였습니다. </p>

<br><br>

### 1. 메인 화면

![main](https://user-images.githubusercontent.com/72599761/144175404-54e796f0-2dd6-4383-aed0-d09999afe852.png)

<br><br>

### 2. 감성 단어 기반 여행 명소 추천시스템

<br>

### (1) 감성 단어 검색

![word_1](https://user-images.githubusercontent.com/72599761/144175426-6f883505-2bfe-4585-bad1-067f036d702d.png)

<br><br>

### (2) 단어와 관련된 Word2Vec 모델 그래프로 시각화  

![word_2](https://user-images.githubusercontent.com/72599761/144175437-44dac374-ad33-4a89-b8c9-c62353727d4c.png)

<br><br>

### (3)  검색 키워드와 유사도가 높은 순으로 서울 내 여행지 10개 추천  

<p> 서울시 25개구 중 원하는 구를 클릭하면 1위부터 10위까지 코사인 유사도가 높은 순으로 여행지 추천합니다. </p> 

<br>

![word_3](https://user-images.githubusercontent.com/72599761/144175446-7143c09e-6ac1-4e97-b4bc-c9394114ff43.png)

<br><br>

### (4) 해당 여행지 클릭하면 상세 정보 확인 가능 

<br>

![word_4](https://user-images.githubusercontent.com/72599761/144175469-ae1abd59-6ee5-4021-8fd6-a127324788d9.png)

<br><br>

### 3. 검색한 여행 명소와 유사한 여행 명소 추천 시스템

<br>

### (1) 여행 명소 검색

![attraction_1](https://user-images.githubusercontent.com/72599761/144175481-6b2ef1d0-fc5c-4c7c-b231-16a302cb1e30.png)

<br><br>

### (2) 검색 키워드와 유사도가 높은 순으로 서울 내 여행지 10개 추천  

<p>코사인 유사도가 1.0에 가까울수록 사용자가 검색한 여행지와 유사한 여행지입니다.</p>

![attraction_2](https://user-images.githubusercontent.com/72599761/144175491-e6ecec26-329d-4922-83f3-88df4ef30103.png)

<br><br>


