/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted, onWillUnmount, useRef } = owl;
import { loadJS } from "@web/core/assets";

const maxDataPoints = 120;

function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

const calculateDynamicMax = (data,ashift=0, percentile = 95) => {
    if (!data || data.length === 0) {
        return null;
    }

    // Extrae los valores 'y' y los ordena
    var vdata = [];
    for(var i = ashift; i < data.length; i++) {
        if (data[i]>0) vdata.push(data[i]);
    }

    console.log(["vdata", vdata, ashift]);

    const yValues =vdata.sort((a, b) => a - b);

    // Calcula el índice del percentil
    const index = Math.ceil((percentile / 100) * yValues.length) - 1;

    // Obtiene el valor en ese índice. Si el índice es -1 (array vacío), devuelve 0.
    let dynamicMax = yValues[index] || 0;

    // Puedes añadir un pequeño "padding" para que el valor más alto del 95% no toque el borde del gráfico
    dynamicMax = dynamicMax * 1.05; // Le damos un 5% de holgura

    // Opcional: Asegúrate de que el máximo siempre sea mayor que el valor máximo de los datos visibles para evitar que la línea de datos se salga del gráfico
    // Esto es útil si el pico se da justo en el 95 percentil
    const trueMax = yValues[yValues.length - 1];
    if (trueMax > dynamicMax) {
        // En este caso, el pico no es "tan raro" y el percentil es muy bajo. Podrías ajustar tu lógica aquí si necesitas.
        // Por ahora, simplemente toma el valor del percentil
    }

    // Se puede redondear a un número "bonito" (ej. 10, 20, 50, 100) para que el gráfico se vea más limpio
    // Por ejemplo, redondeando a la decena más cercana
    return Math.ceil(dynamicMax / 10) * 10;
};

class PPPLineSpeedChart extends Component {
    setup() {
        this.orm = useService("orm");
        this.chartRef = useRef("chart");
        this.chart = null;
        this.hola = "Chao";
        this.interval = null;
        this.down = '';
        this.up = '';
        this.ashift = maxDataPoints;

        onWillStart(async () => {
            await loadJS("https://cdn.jsdelivr.net/npm/chart.js");
        });

        onMounted(() => {
            this.renderChart();
            for(var i = 0; i < maxDataPoints; i++) {
                 this.chart.data.datasets[0].data.push(0);
                 this.chart.data.datasets[1].data.push(0);
                 this.chart.data.labels.push('');
            }
            this.interval = setInterval(this.updateData.bind(this), 1000);
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
        console.log(["resId", lineId]);
        const result = await this.orm.call(
            "silver.netdev.ppp.active.wizard.line",
            "get_interface_speed",
            [lineId]
        );

        if (this.chart) {
            this.chart.data.labels.push('');
          //  this.chart.data.labels.push(new Date().toLocaleTimeString());
            this.chart.data.datasets[0].data.push(result.upload);
            this.chart.data.datasets[1].data.push(result.download);
            this.down = result.download;
            this.up = result.upload;

            this.chart.data.datasets[0].label="Upload: "+formatBytes(this.up);
            this.chart.data.datasets[1].label="Down: "+formatBytes(this.down);

            console.log(["chartee", this.down, this.up, this.chart.data.labels, this.chart.data.datasets]);

            if (this.chart.data.datasets[0].data.length > maxDataPoints) {
                this.ashift = Math.max(this.ashift-1, 0);
                this.chart.data.labels.shift();
                this.chart.data.datasets[0].data.shift();
                this.chart.data.datasets[1].data.shift();
            }


            var m0 = calculateDynamicMax(this.chart.data.datasets[0].data, this.ashift);
            var m1 = calculateDynamicMax(this.chart.data.datasets[1].data, this.ashift);

            console.log(["m", m0, m1]);

                        this.chart.options.scales.y.max = Math.max(m0, m1);
                        // El mínimo puede seguir fijo o ser 0
                        this.chart.options.scales.y.min = 0;


            this.chart.update();
        }
    }

    renderChart() {
        const ctx = this.chartRef.el.getContext('2d');
        console.log(["chart", this.down, this.up]);

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Uploadd '+this.up,
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1,
                    fill: false,
                }, {
                    label: 'Download '+this.down,
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

PPPLineSpeedChart.template = "silver_network.PPPLineSpeedChart";

registry.category("fields").add("ppp_line_speed_chart", {
    component: PPPLineSpeedChart,
});
