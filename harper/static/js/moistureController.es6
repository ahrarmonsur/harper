$(function () { 

    var moistureRequest = $.get("/moisture")
        .done(function(data) {
            renderMoistureChart(data);
        })
        .fail(function() {
            console.log("An error was encountered while retrieving soil moisture data")
        });

    // Set local timezone
    Highcharts.setOptions({
        global: {
            getTimezoneOffset: function (timestamp) {
                return -moment.tz(timestamp, 'America/Toronto').utcOffset();
            }
        }
    });

    var renderMoistureChart = function(data) {

        var moistureChart = Highcharts.chart("moistureGraph", {
            chart: {
                type: "line",
                zoomType: "x",
                panning: true,
                panKey: "shift",
                events: {
                    load: function() {
                        console.log(this);
                        this.xAxis[0].setExtremes(
                            moment().subtract(14, 'days').valueOf(),
                            moment().valueOf()
                        );
                    }
                }

            },
            title: {
                text: "Planter Moisture Content"
            },
            xAxis: {
                type: "datetime",
                title: {
                    text: "Time"
                }
            },
            yAxis: {
                title: {
                    text: "Moisture"
                }
            },
            series: [{
                name: "Paddles",
                data: data
            }]
        });

        return moistureChart;
    };

});
