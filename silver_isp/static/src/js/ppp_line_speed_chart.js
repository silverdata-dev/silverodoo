/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted, onWillUnmount, useRef } = owl;
import { loadJS } from "@web/core/assets";

class PPPLineSpeedChart extends Component {
    setup() {
        this.orm = useService("orm");
        this.chartRef = useRef("chart");
        this.chart = null;
        this.interval = null;

        onWillStart(async () => {
            await loadJS("https://cdn.jsdelivr.net/npm/chart.js");
        });

        onMounted(() => {
            this.renderChart();
            this.interval = setInterval(this.updateData.bind(this), 5000);
        });

        onWillUnmount(() => {
            clearInterval(this.interval);
            if (this.chart) {
                this.chart.destroy();
            }
        });
    }

    async updateData() {
        const lineId = this.props.record.resId;
        const result = await this.orm.call(
            "isp.netdev.ppp.active.wizard.line",
            "get_interface_speed",
            [lineId]
        );

        if (this.chart) {
            this.chart.data.labels.push(new Date().toLocaleTimeString());
            this.chart.data.datasets[0].data.push(result.upload);
            this.chart.data.datasets[1].data.push(result.download);

            const maxDataPoints = 20;
            if (this.chart.data.labels.length > maxDataPoints) {
                this.chart.data.labels.shift();
                this.chart.data.datasets[0].data.shift();
                this.chart.data.datasets[1].data.shift();
            }

            this.chart.update();
        }
    }

    renderChart() {
        const ctx = this.chartRef.el.getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Upload',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1,
                    fill: false,
                }, {
                    label: 'Download',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value, index, values) {
                                if (value >= 1000000) {
                                    return (value / 1000000).toFixed(1) + 'M';
                                } else if (value >= 1000) {
                                    return (value / 1000).toFixed(1) + 'k';
                                }
                                return value;
                            }
                        }
                    }
                }
            }
        });
    }
}

PPPLineSpeedChart.template = "silver_isp.PPPLineSpeedChart";

registry.category("fields").add("ppp_line_speed_chart", {
    component: PPPLineSpeedChart,
});
