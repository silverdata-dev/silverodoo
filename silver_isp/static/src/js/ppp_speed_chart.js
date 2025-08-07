
odoo.define('silver_isp.ppp_speed_chart', function (require) {
'use strict';

var AbstractField = require('web.AbstractField');
var field_registry = require('web.field_registry');
var Highcharts = require('highcharts');

var PppSpeedChart = AbstractField.extend({
    template: 'PppSpeedChart',

    start: function () {
        var self = this;
        this._super.apply(this, arguments);

        // Initial chart rendering
        self._render_chart();

        // Fetch data every 5 seconds
        setInterval(function () {
            self._get_speed_data().then(function (data) {
                self.chart.series[0].setData(data.upload);
                self.chart.series[1].setData(data.download);
            });
        }, 5000);
    },

    _render_chart: function () {
        var self = this;
        this._get_speed_data().then(function (data) {
            self.chart = Highcharts.chart(self.el, {
                chart: {
                    type: 'spline',
                    animation: Highcharts.svg, // don't animate in old IE
                    marginRight: 10,
                },
                title: {
                    text: 'Live PPP Speed'
                },
                xAxis: {
                    type: 'datetime',
                    tickPixelInterval: 150
                },
                yAxis: {
                    title: {
                        text: 'Speed'
                    },
                    plotLines: [{
                        value: 0,
                        width: 1,
                        color: '#808080'
                    }]
                },
                tooltip: {
                    formatter: function () {
                        return '<b>' + this.series.name + '</b><br/>' +
                            Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                            Highcharts.numberFormat(this.y, 2) + ' kbps';
                    }
                },
                legend: {
                    enabled: true
                },
                exporting: {
                    enabled: false
                },
                series: [{
                    name: 'Upload',
                    data: data.upload
                }, {
                    name: 'Download',
                    data: data.download
                }]
            });
        });
    },

    _get_speed_data: function () {
        var self = this;
        return this._rpc({
            model: 'isp.router.ppp.active.wizard',
            method: 'get_speed_data',
            args: [self.record.data.id],
        });
    }
});

field_registry.add('ppp_speed_chart', PppSpeedChart);

return PppSpeedChart;
});
