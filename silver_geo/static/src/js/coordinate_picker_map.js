/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { CharField } from "@web/views/fields/char/char_field";

const { Component, onWillStart, onMounted, useState, useRef } = owl;

// This is the component that will be rendered inside the modal
export class CoordinatePickerMap extends Component {
    static template = "silver_geo.CoordinatePickerMap";

    setup() {
        this.orm = useService("orm");
        this.mapContainer = useRef("map-container");
        this.state = useState({
            lat: this.props.lat || -17.3894997, // Default to Cochabamba
            lon: this.props.lon || -66.1568000,
        });

        onWillStart(async () => {
            await loadJS("https://openlayers.org/en/v6.5.0/build/ol.js");
        });

        onMounted(() => {
            this.initMap();
        });
    }

    initMap() {
        const initialCoords = [this.state.lon, this.state.lat];
        const transformedCoords = ol.proj.fromLonLat(initialCoords);

        this.markerSource = new ol.source.Vector();
        const markerStyle = new ol.style.Style({
            image: new ol.style.Icon({
                anchor: [0.5, 1],
                src: '/silver_geo/static/src/img/map_icons/cto.png',
                scale: 0.08,
            }),
        });

        this.marker = new ol.Feature({
            geometry: new ol.geom.Point(transformedCoords),
        });
        this.markerSource.addFeature(this.marker);

        this.map = new ol.Map({
            target: this.mapContainer.el,
            layers: [
                new ol.layer.Tile({ source: new ol.source.OSM() }),
                new ol.layer.Vector({ source: this.markerSource, style: markerStyle }),
            ],
            view: new ol.View({ center: transformedCoords, zoom: 15 }),
        });

        this.map.on("singleclick", (evt) => {
            const coords = ol.proj.toLonLat(evt.coordinate);
            this.state.lon = coords[0];
            this.state.lat = coords[1];
            this.marker.getGeometry().setCoordinates(evt.coordinate);
        });
    }

    async onSave() {
        await this.orm.write("silver.node", [this.props.resId], {
            gps_lat: this.state.lat,
            gps_lon: this.state.lon,
        });
        this.props.close(); // Close the dialog
    }

    onCancel() {
        this.props.close(); // Close the dialog
    }
}

// This is the new Field Widget that will be placed on the form view
export class CoordinatePickerWidget extends Component {
    static template = xml`
        <button t-on-click="openMap" class="btn btn-link o_icon_button fa fa-map-marker" aria-label="Seleccionar Coordenadas"/>
    `;

    setup() {
        this.dialog = useService("dialog");
        this.orm = useService("orm");
    }

    async openMap() {
        const recordData = await this.orm.read(
            this.props.record.resModel,
            [this.props.record.resId],
            ["gps_lat", "gps_lon"]
        );

        this.dialog.add(CoordinatePickerMap, {
            title: "Seleccionar Coordenadas",
            resId: this.props.record.resId,
            lat: recordData[0].gps_lat,
            lon: recordData[0].gps_lon,
        }, {
            onClose: () => {
                // This will reload the view to show the new coordinates
                this.props.record.load();
            }
        });
    }
}

// Register the new widget in the field registry
registry.category("fields").add("coordinate_picker_widget", {
    component: CoordinatePickerWidget,
});