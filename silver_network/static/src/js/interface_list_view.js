/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { useInterval } from "@web/core/utils/timing";
import { jsonrpc } from "@web/core/network/rpc_service";
import { onWillUnmount, onMounted, useState } from "@odoo/owl";

export class InterfaceListRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.state = useState({
            trafficData: {},
        });

        // Update every 3 seconds
        useInterval(() => this.fetchTrafficData(), 3000);

        onMounted(() => this.fetchTrafficData());
    }

    get netdevId() {
        // Find the netdev_id from the form's context
        return this.props.list.context.active_id;
    }

    async fetchTrafficData() {
        const interfaceNames = this.props.list.records.map(rec => rec.data.name);
        if (!interfaceNames.length) {
            return;
        }

        const data = await jsonrpc('/silver_network/get_interface_stats', {
            netdev_id: this.netdevId,
            interface_names: interfaceNames,
        });

        if (data && !data.error) {
            this.state.trafficData = data;
            // Update the records in place to trigger re-render
            for (const record of this.props.list.records) {
                const ifaceName = record.data.name;
                if (this.state.trafficData[ifaceName]) {
                    record.data.rx_speed = this.state.trafficData[ifaceName].rx_speed;
                    record.data.tx_speed = this.state.trafficData[ifaceName].tx_speed;
                }
            }
        } else if (data.error) {
            console.error("Error fetching interface stats:", data.error);
        }
    }
}

export const InterfaceListView = {
    ...listView,
    Renderer: InterfaceListRenderer,
};

registry.category("views").add("interface_list_view", InterfaceListView);
