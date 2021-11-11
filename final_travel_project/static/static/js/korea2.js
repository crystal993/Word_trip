window.onload = function() {
    drawMap('#container');
};

//지도 그리기
function drawMap(target) {
    var width = 700; //지도의 넓이
    var height = 700; //지도의 높이

    var labels;

    var projection = d3.geo.mercator()
        .center([126.9895, 37.5651])
        .scale(90000)
        .translate([width/2, height/2]);
    var path = d3.geo.path().projection(projection);

    var zoom = d3.behavior
        .zoom()
        .translate(projection.translate())
        .scale(projection.scale())
        .scaleExtent([height, 800 * height])
        .on('zoom', zoom);

    var svg = d3
        .select(target)
        .append('svg')
        .attr('width', width + 'px')
        .attr('height', height + 'px')
        .attr('id', 'map')
        .attr('class', 'map');

    /* 줌이벤트랑 클릭이벤트 발생 : 보류 */
    var states = svg
        .append('g')
        .attr('id', 'states')
        .call(zoom);

    states
        .append('rect')
        .attr('class', 'background')
        .attr('width', width + 'px')
        .attr('height', height + 'px');

    //geoJson데이터를 파싱하여 지도그리기
    d3.json('/static/json/seoul_map2.geojson', function(json) {
        states
            .selectAll('path') //지역 설정
            .data(json.features)
            .enter()
            .append('path')
            .attr('d', path)
            .attr('id', function(d) {
                return 'path-' + d.properties.SIG_KOR_NM;
            })
            .on("click", function(d){location.href='/attraction/detail2_place/'+d.properties.SIG_KOR_NM});
                /* 클릭했을때 이동과 얼랏창*/
                /*location.href='/nationWide/detail/{{s.rk}}'*/
                /*{alert(d.properties.SIG_KOR_NM +" 클릭 이벤트");});*/
        labels = states
            .selectAll('text')
            .data(json.features) //라벨표시
            .enter()
            .append('text')
            .attr('transform', translateTolabel)
            .attr('id', function(d) {
                return 'label-' + d.properties.SIG_KOR_NM;
            })
            .attr('text-anchor', 'middle')
            .attr('dy', '.35em')
            .text(function(d) {
                return d.properties.SIG_KOR_NM;
            });
    });

    //텍스트
    function translateTolabel(d) {
        var arr = path.centroid(d);
        return 'translate(' + arr + ')';
    }

    function zoom() {
        projection.translate(d3.event.translate).scale(d3.event.scale);
        states.selectAll('path').attr('d', path);
        labels.attr('transform', translateTolabel);
    }
}