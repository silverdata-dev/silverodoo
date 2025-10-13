/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, onWillUnmount } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

// This component is a "trigger". It has no template and renders nothing.
// Its only job is to start and stop the polling logic for the entire wizard.
export class InterfaceSpeedUpdater extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.updateInterval = null;

        this.rx_speed = this.props.rx_speed;
        this.tx_speed = this.props.tx_speed;
        this.record = this.props.record;
        this.r = this.props.r;
        var self = this;

        onMounted(() => {
             console.log(["kola", this.record, this.r]);
            // The DOM is ready, we can start our manual process.
            this.startPolling();
        });

        onWillUnmount(() => {
            // The user closed the wizard, so we stop polling to prevent memory leaks.
            this.stopPolling();
        });
    }

    startPolling() {
        // Find the netdev_id from the form's context, passed by the Python button.
        //const netdevId = this.props.record.context.active_id;
        const netdevId = this.record.evalContext.context.default_netdev_id;
        if (!netdevId) {
            console.error("InterfaceSpeedUpdater: netdev_id not found in context.");
            return;
        }

        console.log(["netdev ", netdevId]);

        this.updateInterval = setInterval(async () => {
            // 1. Find all visible interface names from all tables in the DOM
            const interfaceNames = new Set(); // Use a Set to avoid duplicates
            const allRows = document.querySelectorAll('.o_form_view .o_notebook tbody tr.o_data_row');
//            this.record.data.line_ids.records.forEach(r => {
//                interfaceNames.add(r.data.name);
//            });
            allRows.forEach(row => {
                 const nameCell = row.querySelector('td[name="name"]');
                if (nameCell && nameCell.textContent) {
                    interfaceNames.add(nameCell.textContent);
                }
            })

        console.log(["interfaceNames ", interfaceNames]);


            const names = [...interfaceNames];
            if (names.length === 0) {
                return; // Nothing to update
            }

            // 2. Call the existing RPC endpoint to get fresh data
            const trafficData = await this.rpc("/silver_network/get_interface_stats", {
                netdev_id: netdevId,
                interface_names: names,
            });

            if (!trafficData || trafficData.error) {
                console.error("Error fetching interface stats:", trafficData.error);
                this.stopPolling(); // Stop if there's an error
                return;
            }

            // 3. Manually update the DOM with the new speeds
            allRows.forEach(row => {
                const nameCell = row.querySelector('td[name="name"]');
                if (nameCell && nameCell.textContent) {
                    const interfaceName = nameCell.textContent;
                    const data = trafficData[interfaceName];
                    if (data) {
                        const rxCell = row.querySelector('td[name="rx_speed"]');
                        const txCell = row.querySelector('td[name="tx_speed"]');
                        if (rxCell) rxCell.textContent = data.rx_speed;
                        if (txCell) txCell.textContent = data.tx_speed;
                    }
                }
            });

        }, 1500); // Update every 3 seconds
    }

    stopPolling() {
        console.log("stop");
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Explicitly link the component to its template
InterfaceSpeedUpdater.template = "silver_network.InterfaceSpeedUpdater";

// Register the component as a new field widget
//registry.category("fields").add("interface_speed_updater", {
//    component: InterfaceSpeedUpdater,
//});



//InterfaceSpeedUpdater.template = "silver_network.InterfaceSpeedUpdater";
InterfaceSpeedUpdater.props = {
    ...standardFieldProps,
    record: { type: Object },
    options: { type: Object , optional: true},
    r: { type: String, optional: true},
    readonly: { type: Boolean, optional: true },
    rx_speed: { type: String, optional: true },
    tx_speed: { type: String, optional: true },
};

registry.category("fields").add("interface_speed_updater", {
    component: InterfaceSpeedUpdater,
    extractProps: ({ attrs }) => ({
        rx_speed: attrs.rx_speed,
        tx_speed: attrs.tx_speed,
    }),
});

