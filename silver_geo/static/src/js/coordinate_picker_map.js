/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useRecordObserver } from "@web/model/relational_model/utils";

const { Component, onMounted, onWillUnmount, useRef } = owl;

export class CoordinatePickerMap extends Component {
    setup() {
        this.map = null;
        this.marker = null;
        this.mapContainer = useRef("mapContainer");
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

    initializeMap() {
        if (!this.mapContainer.el) return;

        const initialLat = this.record.data[this.latField] || 9.02497;
        const initialLng = this.record.data[this.lngField] || -66.41375;
        
        this.map = L.map(this.mapContainer.el, { maxZoom: 19 }).setView([initialLat, initialLng], 6);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(this.map);

        this.marker = L.marker([initialLat, initialLng], { 
            // Only allow dragging if the form is NOT readonly
            draggable: !this.props.readonly,
        }).addTo(this.map);

        // Only attach event listeners if the form is NOT readonly
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
                console.log(["lng", position.lng, "lat", position.lat, this.lngField, this.latField, this.record]);

                this.record.update({
                    [this.lngField]: position.lng,
                    [this.latField]: position.lat,
                });
            });
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