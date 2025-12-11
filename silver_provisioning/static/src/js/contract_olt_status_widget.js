/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";

class ContractOltStatus extends Component {
    setup() {
        super.setup();
        this.state = useState({
            olt_state: this.props.record.data.olt_state,
            wan_state: this.props.record.data.wan_state
        });
        onMounted(() => this.startPolling());
        onWillUnmount(() => this.stopPolling());
    }

    async startPolling() {
        this.timer = setInterval(async () => {
            // Use the modern ORM service available in the field component props
            const result = await this.props.record.model.orm.call(
                'silver.contract',
                'action_check_olt_state_for_js',
                [[this.props.record.resId]],
            );
            if (result) {
                let changed = false;
                if (this.state.olt_state !== result.olt_state) {
                    this.state.olt_state = result.olt_state;
                    changed = true;
                }
                if (this.state.wan_state !== result.wan_state) {
                    this.state.wan_state = result.wan_state;
                    changed = true;
                }
                // The view will automatically re-render due to the state change,
                // but we need to reload the record to get other potential updates.
                if (changed) {
                    await this.props.record.load();
                }
            }
        }, 10000); // Poll every 10 seconds
    }

    stopPolling() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }
}

ContractOltStatus.template = 'silver_provisioning.ContractOltStatus';
ContractOltStatus.props = {
    record: { type: Object },
};

registry.category("fields").add("contract_olt_status", {
    component: ContractOltStatus,
});

