/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
import { onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

console.log("Realtime Interface JS File Loaded");

class RealtimeInterfaceListController extends ListController {
    setup() {
        super.setup();
        console.log("RealtimeInterfaceListController setup initiated.");

        //this.rpc = useService("rpc");
        this.updateInterval = null;

        // Get netdev_id from the form's record data
        this.netdevId = this.props.context.default_netdev_id || this.props.context.active_id;
        console.log(`netdev_id found: ${this.netdevId}`);

        onMounted(() => {
            console.log("Component Mounted. Starting polling.");
            this.startPolling();
        });

        onWillUnmount(() => {
            console.log("Component Will Unmount. Stopping polling.");
            this.stopPolling();
        });
    }

    startPolling() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        // Poll every 3 seconds
        this.updateInterval = setInterval(async () => {
            console.log("Polling for new interface data...");
            if (!this.netdevId || this.model.root.records.length === 0) {
                console.log("Skipping poll: No netdev_id or no records.");
                return;
            }

            const interfaceNames = this.model.root.records.map(rec => rec.data.name);
            if (interfaceNames.length === 0) {
                return;
            }

            try {
                const trafficData = await rpc("/silver_network/get_interface_stats", {
                    netdev_id: this.netdevId,
                    interface_names: interfaceNames,
                });

                if (trafficData && !trafficData.error) {
                    // This is the key part: we reload the model, which will
                    // automatically trigger a re-render of the view.
                    await this.model.load();
                } else if (trafficData && trafficData.error) {
                    console.error("Error fetching interface stats:", trafficData.error);
                    this.stopPolling(); // Stop on error
                }
            } catch (e) {
                console.error("RPC call failed:", e);
                this.stopPolling();
            }
        }, 3000);
    }

    stopPolling() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            console.log("Polling stopped.");
        }
    }
}

export const RealtimeInterfaceListView = {
    ...listView,
    Controller: RealtimeInterfaceListController,
};

console.log("Registering 'realtime_interface_list' view.");
registry.category("views").add("realtime_interface_list", RealtimeInterfaceListView);
