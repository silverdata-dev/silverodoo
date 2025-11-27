/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted, useRef } = owl;

export class NodeMapWidget extends Component {
    static template = "silver_geo.NodeMap";

    setup() {
        this.rpc = useService("rpc");
        this.mapRef = useRef("map");

        onWillStart(async () => {
            await this.loadLeaflet();
        });

        onMounted(() => {
            this.render_map();
        });
    }

    async loadLeaflet() {
        if (typeof L === 'undefined') {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css';
            document.head.appendChild(link);

            return new Promise((resolve) => {
                const script = document.createElement('script');
                script.src = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js';
                script.onload = resolve;
                document.head.appendChild(script);
            });
        }
        return Promise.resolve();
    }

    async render_map() {
        const data = await this.rpc('/silver_geo/get_assets', {
            node_id: this.props.record.resId,
        });

        const container = this.mapRef.el;
        const map = L.map(container).setView([10.50, -66.91], 13); // Default view

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        data.assets.forEach(asset => {
            if (asset.latitude && asset.longitude) {
                L.marker([asset.latitude, asset.longitude])
                    .addTo(map)
                    .bindPopup(`<b>${asset.name}</b><br>${asset.model}`);
            }
        });

        if (data.center_on) {
            map.setView([data.center_on.lat, data.center_on.lon], 16);
        }
    }
}

registry.category("fields").add("node_map", {
    component: NodeMapWidget,
});