/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { onWillUnmount, onMounted, useRef, onWillStart } from "@odoo/owl";
import { jsonrpc } from "@web/core/network/rpc_service";
import { loadJS } from "@web/core/assets";

const { Component } = owl;

export class SystemInfoChartWidget extends Component {
    setup() {
        this.chart = null;
        this.canvasRef = useRef("canvas");
        this.interval = null;

         onWillStart(async () => {
            await loadJS("https://cdn.jsdelivr.net/npm/chart.js");
        });


        onMounted(() => {
            this.renderChart();
            this.interval = setInterval(this.updateChart.bind(this), 2000); // Update every 2 seconds
        });

        onWillUnmount(() => {
            clearInterval(this.interval);
            if (this.chart) {
                this.chart.destroy();
            }
        });
    }

    get netdevId() {
        return this.props.record.data.netdev_id[0];
    }

    renderChart() {
        const ctx = this.canvasRef.el.getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [], // Timestamps
                datasets: [{
                    label: 'CPU Load (%)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    yAxisID: 'y',
                }, {
                    label: 'RAM Usage (%)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    yAxisID: 'y',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Usage (%)'
                        }
                    },
                    x: {
                         ticks: {
                            display: false // Hide x-axis labels (timestamps) for clarity
                        }
                    }
                },
                animation: {
                    duration: 500 // Smoother animation
                }
            }
        });
    }

    async updateChart() {
        const data = await jsonrpc('/silver_network/get_system_stats', { netdev_id: this.netdevId });

        if (data.error) {
            console.error("Error fetching system stats:", data.error);
            // Optional: Display an error message on the UI
            return;
        }

        const now = new Date();
        const label = now.toLocaleTimeString();

        // Add new data
        this.chart.data.labels.push(label);
        this.chart.data.datasets[0].data.push(data.cpu_load);
        this.chart.data.datasets[1].data.push(data.ram_usage);

        // Limit the number of data points to keep the chart readable
        const maxDataPoints = 30;
        if (this.chart.data.labels.length > maxDataPoints) {
            this.chart.data.labels.shift();
            this.chart.data.datasets.forEach((dataset) => {
                dataset.data.shift();
            });
        }

        this.chart.update();
    }
}

SystemInfoChartWidget.template = "silver_network.SystemInfoChartWidget";

registry.category("fields").add("system_info_chart", {
    component: SystemInfoChartWidget,
});
