function makeNewChart ( title, container, dataPoints ) {
    var chart = new CanvasJS.Chart(container,{
        title :{
            text: title
        },			
        animationEnabled: true,
        data: [{
            type: "area",
            xValueType: "dateTime",
            dataPoints: dataPoints
        }]
    });
    return chart;
};

function getSeriesData( dataPoints, mode, target, seconds ) {

    if ( mode === 'sensor' ) {
        $.get('/api/gas/reading/get',
            { seconds: seconds, sensor_id: target },
            function ( data ) {
            
            $.each(data.readings, function(i,reading){
                timestamp = reading.created.$date;
                value = reading.value;
                dataPoints.push({ x: timestamp, y: value});
            });

        });
    }
    setTimeout(function(){getSeriesData(dataPoints, mode, target, seconds)},
        seconds * 1000);
};

function renderChart( dataPoints, chart, interval, dataLength ) {
    if (dataPoints.length > dataLength)
    {
        dataPoints.shift();
    }
    chart.render();
    setTimeout(function(){renderChart(dataPoints, chart, interval, dataLength)},
            interval);
};
