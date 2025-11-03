odoo.define('silver_network.queue_traffic_graph', function (require) {
    "use strict";

    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var QWeb = core.qweb;

    // 1. Lógica del Gráfico en un Diálogo
    function createTrafficChartDialog(line_id) {
        var self = this;
        var chart;
        var chartUpdateInterval;

        var dialog = new Dialog(this, {
            title: _t("Queue Real-Time Traffic"),
            $content: $(QWeb.render("silver_network.QueueTrafficChartContainer")),
            buttons: [{
                text: _t("Close"),
                close: true,
                click: function () {
                    clearInterval(chartUpdateInterval); // Detener el bucle al cerrar
                }
            }],
        }).open();

        dialog.opened().then(function () {
            var ctx = dialog.$('.queue_traffic_chart')[0].getContext('2d');
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: _t('Upload (bps)'),
                        data: [],
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }, {
                        label: _t('Download (bps)'),
                        data: [],
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    animation: {
                        duration: 500 // Animación más suave
                    }
                }
            });

            // Iniciar el bucle para actualizar el gráfico
            chartUpdateInterval = setInterval(function () {
                self._rpc({
                    model: 'silver.netdev.queue.wizard.line',
                    method: 'get_queue_traffic_data',
                    args: [line_id],
                }).then(function (data) {
                    if (chart.data.labels.length > 20) { // Mantener solo 20 puntos de datos
                        chart.data.labels.shift();
                        chart.data.datasets[0].data.shift();
                        chart.data.datasets[1].data.shift();
                    }
                    var now = new Date();
                    chart.data.labels.push(now.toLocaleTimeString());
                    chart.data.datasets[0].data.push(data.upload);
                    chart.data.datasets[1].data.push(data.download);
                    chart.update();
                });
            }, 2000); // Actualizar cada 2 segundos
        });
    }

    // 2. Extender el ListController para manejar el clic del botón
    var QueueListController = ListController.extend({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
        },

        _onOpenSpeedChart: function (ev) {
            ev.preventDefault();
            var $target = $(ev.currentTarget);
            var line_id = $target.data('line-id');
            
            // Llamar a la función que crea y gestiona el diálogo del gráfico
            createTrafficChartDialog.call(this, line_id);
        },

        /**
         * @override
         */
        _renderRow: function ($tr, record) {
            var self = this;
            this._super.apply(this, arguments);
            // Adjuntar el evento de clic al botón específico de esta fila
            $tr.find('.btn-open-queue-chart').on('click', this._onOpenSpeedChart.bind(this));
            return $tr;
        }
    });

    // 3. Crear una nueva Vista de Lista que use nuestro Controller personalizado
    var QueueListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: QueueListController,
        }),
    });

    // 4. Registrar la nueva vista para que Odoo pueda usarla
    viewRegistry.add('queue_traffic_list', QueueListView);

    // 5. Añadir la plantilla QWeb para el contenedor del gráfico
    core.qweb.add_template('/silver_network/static/src/xml/queue_traffic_graph_template.xml');

});
