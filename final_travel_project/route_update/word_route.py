from flask import Flask, request, render_template, redirect, Blueprint
import models as mo
import json

bp = Blueprint('word', __name__, url_prefix='/word')

reviewService = mo.ReviewService()
mapService = mo.MapService()

@bp.route('/main', methods=['POST', 'GET'])
def word_main():
    closeSiteList = mapService.getCloseSiteList()
    return render_template('word/main.html', closeSiteList=closeSiteList)

@bp.route('/word_info', methods=['POST', 'GET'])
def word_info():
    searchWord = request.form['word']
    myWordList = reviewService.keword_similar(searchWord) #그래프와 리뷰 서비스 둘다에 필요한 기능이라
    reviewService.keyword_recommend(myWordList)
    myGraphVec = reviewService.keywordScatterGraph(myWordList, searchWord)

    # 이 벡터를 시각화할 수 있도록  PCA를 불러온다.
    # 원래는 차원이 매우 높아서 단어가 임베딩 공간을 차지하는 방식을 시각화하는 것이 불가능함.
    # PCA는 일반적으로 단어 임베딩의 차원을 줄여서 시각화하는 역할.
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)  # 2D로 시각화
    xy_axis = pca.fit_transform(myGraphVec)  # 단어 임베딩 차원(단어갯수만큼존재할것임)을 2개(x축,y축)로 만들어줌.
    x_axis = xy_axis[:, 0]  # x축
    y_axis = xy_axis[:, 1]  # y축

    import matplotlib.pyplot as plt
    # 한글 폰트 사용을 위해서 세팅
    from matplotlib import font_manager, rc
    font_path = "C:/Windows/Fonts/H2GTRM.TTF"  # 한글고딕
    font = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font)  # 한글폰트 설정

    import plotly # plotly, 다른 그래프 라이브러리보다 예쁨.
    import plotly.graph_objects as go

    fig = go.Figure(data=go.Scatter(x=x_axis,  # x축
                                    y=y_axis,  # y축
                                    mode='markers+text',
                                    text=myWordList))

    fig.update_layout(title=f'Word Trip {searchWord} Word2Vec')

    import plotly.io as pio  # 입출력 라이브러리

    graph = pio.to_json(fig) #그래프를 json형태로 만듬.
    graph = graph.encode('utf-8') # 한글 인코딩 한글->숫자
    graph = graph.decode('unicode_escape') #다시 한글로 디코딩

    # json을 html로 뿌릴 때 필요
    graphJSON = json.dumps(graph, ensure_ascii=False , cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('word/wordInfo.html', graphJSON=graphJSON)

@bp.route('/detail/<string:guname>', methods=['POST', 'GET']) #<a href="/board/detail/{{b.num}}">
def detail(guname):
    a = guname
    b = reviewService.mapReview(a)
    return render_template('word/wordInfo.html', b=b, guname=guname)

@bp.route('/detail/detail/<string:place_name>', methods=['POST', 'GET']) #'/attraction/detail/3'
def get(place_name):
    p = reviewService.getAttrByName(place_name)
    r = reviewService.getAttrByReview(place_name)
    return render_template('word/detail.html', p=p, r=r)