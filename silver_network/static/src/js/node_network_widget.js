/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted, useRef } = owl;

export class NodeNetworkWidget extends Component {
    static template = "silver_network.NodeNetwork";

    setup() {
        this.rpc = useService("rpc");
        this.graphRef = useRef("graph");

        onWillStart(async () => {
            await this.loadVisNetwork();
        });

        onMounted(() => {
            this.render_network();
        });
    }

    async loadVisNetwork() {
        if (typeof vis === 'undefined') {
            return new Promise((resolve) => {
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/vis-network/standalone/umd/vis-network.min.js';
                script.onload = resolve;
                document.head.appendChild(script);
            });
        }
        return Promise.resolve();
    }

    async render_network() {
        const data = await this.rpc('/silver_network/get_node_hierarchy', {
            node_id: this.props.record.resId,
        });

        const container = this.graphRef.el;
        const nodes = new vis.DataSet(data.nodes);
        const edges = new vis.DataSet(data.edges);
        const network_data = {
            nodes: nodes,
            edges: edges,
        };
        const options = {
            nodes: {
                shape: 'dot',
                size: 16,
            },
            physics: {
                forceAtlas2Based: {
                    gravitationalConstant: -26,
                    centralGravity: 0.005,
                    springLength: 230,
                    springConstant: 0.18,
                },
                maxVelocity: 146,
                solver: 'forceAtlas2Based',
                timestep: 0.35,
                stabilization: { iterations: 150 },
            },
        };
        new vis.Network(container, network_data, options);
    }
}

registry.category("fields").add("node_network", {
    component: NodeNetworkWidget,
});