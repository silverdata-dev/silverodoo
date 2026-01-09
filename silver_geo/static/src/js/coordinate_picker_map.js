/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useRecordObserver } from "@web/model/relational_model/utils";
import { useService } from "@web/core/utils/hooks";

const { Component, onMounted, onWillUnmount, useRef } = owl;

export class CoordinatePickerMap extends Component {
    setup() {
        this.map = null;
        this.marker = null;
        this.mapContainer = useRef("mapContainer");
        this.rpc = useService("rpc"); // RPC service for calling the controller

        this.latField = this.props.latitude_field;
        this.lngField = this.props.longitude_field;
        this.record = this.props.record;

        useRecordObserver(() => {
            const newLat = this.record.data[this.latField];
            const newLng = this.record.data[this.lngField];
            this.updateMarkerPosition(newLng, newLat);
        });

        onMounted(() => {
            setTimeout(() => this.initializeMap(), 0);
        });

        onWillUnmount(() => {
            if (this.map) {
                this.map.remove();
            }
        });
    }

    async initializeMap() {
        if (!this.mapContainer.el) return;

        const initialLat = this.record.data[this.latField] || 9.02497;
        const initialLng = this.record.data[this.lngField] || -66.41375;
        
        this.map = L.map(this.mapContainer.el, { maxZoom: 19 }).setView([initialLat, initialLng], 13); // Zoom in a bit more

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
         //   attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(this.map);

        this.marker = L.marker([initialLat, initialLng], { 
            draggable: !this.props.readonly,
        }).addTo(this.map);

        if (!this.props.readonly) {
            this.marker.on('dragend', (event) => {
                const position = this.marker.getLatLng();
                this.record.update({
                    [this.lngField]: position.lng,
                    [this.latField]: position.lat,
                });
            });

            this.map.on('click', (event) => {
                const position = event.latlng;
                this.marker.setLatLng(position);
                this.record.update({
                    [this.lngField]: position.lng,
                    [this.latField]: position.lat,
                });
            });
        }

        // Load and display assets on the map
        await this.loadAssetsOnMap();
    }

    async loadAssetsOnMap() {
        const response = await this.rpc('/silver_geo/get_assets', {});
        const assets = response.assets || [];
        
        // Optional: Define different icons for different asset types
        const icons = {
            node: L.icon({ iconUrl: '/web/static/src/img/markers/marker-gold.png', shadowUrl: '/web/static/src/img/markers/marker-shadow.png', iconSize: [25, 41], iconAnchor: [12, 41] }),
            box: L.icon({ iconUrl: '/web/static/src/img/markers/marker-green.png', shadowUrl: '/web/static/src/img/markers/marker-shadow.png', iconSize: [25, 41], iconAnchor: [12, 41] }),
            default: L.icon({ iconUrl: '/web/static/src/img/markers/marker-blue.png', shadowUrl: '/web/static/src/img/markers/marker-shadow.png', iconSize: [25, 41], iconAnchor: [12, 41] })
        };

        for (const asset of assets) {
                 var nmodel = asset.nmodel.replaceAll(".", "_");
            if (asset.latitude && asset.longitude && ['box', 'node'].includes(nmodel)) {
                const icon = L.icon({iconUrl:`/silver_geo/static/src/img/map_icons/${nmodel}.png`,  iconSize: [25, 41], iconAnchor: [12, 41] });
                //const icon = icons[asset.model] || icons.default;
                L.marker([asset.latitude, asset.longitude], { icon: icon, opacity: 0.7 })
                    .bindPopup(`<b>${asset.nmodel.toUpperCase()}:</b><br/>${asset.name}`)
                    .addTo(this.map);
            }
        }
    }

    updateMarkerPosition(lng, lat) {
        const newLatLng = L.latLng(lat || 0, lng || 0);
        if (this.map && this.marker && !this.marker.getLatLng().equals(newLatLng)) {
            this.marker.setLatLng(newLatLng);
            this.map.panTo(newLatLng);
        }
    }
}

CoordinatePickerMap.template = "silver_geo.CoordinatePickerMap";
CoordinatePickerMap.props = {
    record: { type: Object },
    readonly: { type: Boolean, optional: true },
    latitude_field: { type: String },
    longitude_field: { type: String },
};

registry.category("view_widgets").add("coordinate_picker_map", {
    component: CoordinatePickerMap,
    extractProps: ({ attrs }) => ({
        latitude_field: attrs.latitude_field,
        longitude_field: attrs.longitude_field,
    }),
});
