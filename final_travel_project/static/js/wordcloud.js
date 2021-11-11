window.onload = function() {
    drawcord('#wordcloud');
};

function drawcord(target) {
    var width = 1000,
        height = 350

    d3.csv("/static/js/worddata.csv", function (data) {
        showCloud(data)
        setInterval(function(){
             showCloud(data)
        },4000)
    });

    //scale.linear: 선형적인 스케일로 표준화를 시킨다.
    //domain: 데이터의 범위, 입력 크기
    //range: 표시할 범위, 출력 크기
    //clamp: domain의 범위를 넘어간 값에 대하여 domain의 최대값으로 고정시킨다.
    wordScale = d3.scale.linear().domain([0, 200]).range([0, 200]).clamp(true);
    var keywords = ["힐링","자연","데이트","쇼핑","카페","하늘","자전거","아기","야경","travel","드라이브"]
    var svg = d3.select("svg")
                .append("g")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")

    function showCloud(data) {
        d3.layout.cloud().size([width, height])
            //클라우드 레이아웃에 데이터 전달
            .words(data)
            .rotate(function (d) {
                return d.text.length > 3 ? 10 : 0;
            })
            //스케일로 각 단어의 크기를 설정
            .fontSize(function (d) {
                return wordScale(d.frequency);
            })
            //클라우드 레이아웃을 초기화 > end이벤트 발생 > 연결된 함수 작동
            .on("end", draw)
            .start();

        function draw(words) {
            var cloud = svg.selectAll("text").data(words)
            //Entering words
            cloud.enter()
                .append("text")
                .style("fonts", "FontAwesome-webfont.woff2")
                .style("fill", function (d) {
                    return (keywords.indexOf(d.text) > -1 ? "#fbc280" : "#405275");
                })
                .style("fill-opacity", .5)
                .attr("text-anchor", "middle")
                .attr('font-size', 1)
                .text(function (d) {
                    return d.text;
                });
            cloud
                .transition()
                .duration(9)
                .style("font-size", function (d) {
                    return d.size + "px";
                })
                .attr("transform", function (d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                })
                .style("fill-opacity", 5);
        }
    }
}