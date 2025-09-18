/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted, onWillUnmount, useRef } = owl;
import { loadJS } from "@web/core/assets";

class PPPSpeedChart extends Component {
    setup() {
        this.orm = useService("orm");
        this.chartRef = useRef("chart");
        this.chart = null;
        this.hola = "uouer";
//        this.data = [];
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
        const wizardId = this.props.record.resId;
        const result = await this.orm.call(
            "silver.netdev.ppp.active.wizard",
            "get_speed_data",
            [wizardId]
        );

        if (this.chart) {
            // Add new data point
            this.chart.data.labels.push(new Date().toLocaleTimeString());
            this.chart.data.datasets[0].data.push(result[0]);

            // Optional: Limit the number of data points shown
            const maxDataPoints = 20;
            if (this.chart.data.labels.length > maxDataPoints) {
                this.chart.data.labels.shift();
                this.chart.data.datasets[0].data.shift();
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
                    label: 'Speed',
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
                                let max = Math.max(...values.map(v => v.value));
                                if (max > 1000000) {
                                    return (value / 1000000).toFixed(1) + 'M';
                                } else if (max > 1000) {
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

PPPSpeedChart.template = "silver_network.PPPSpeedChart";

registry.category("fields").add("ppp_speed_chart", {
    component: PPPSpeedChart,
});