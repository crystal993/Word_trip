from flask import Flask, request, render_template, redirect, Blueprint
import models as mo

bp = Blueprint('attraction', __name__, url_prefix='/attraction')

reviewService = mo.ReviewService()
mapService = mo.MapService()

@bp.route('/main', methods=['POST', 'GET'])
def attraction_main():
    closeSiteList = mapService.getCloseSiteList()
    return render_template('attraction/main.html', closeSiteList=closeSiteList)

@bp.route('/place_recommend', methods=['POST'])
def place_recommand():
    searchPlace = request.form['place']
    a = reviewService.place_recommend(searchPlace)

    return render_template('attraction/place_recommend.html')

@bp.route('/detail2_place/<string:guname>', methods=['POST', 'GET'])
def detail2_place(guname):
    a = guname
    place = reviewService.mapPlace(a)

    return render_template('attraction/place_recommend.html', place=place, guname=guname)

# 장소 검색 페이지
@bp.route('/index_2_place', methods=['POST', 'GET'])
def index_2_place():
    return render_template('nationWide/index_2_place.html')

@bp.route('/detail/detail/<string:place_name>', methods=['POST', 'GET']) #'/attraction/detail/3'
def get(place_name):
    p = reviewService.getAttrByName(place_name)
    r = reviewService.getAttrByReview(place_name)

    return render_template('attraction/detail.html', p=p, r=r)
