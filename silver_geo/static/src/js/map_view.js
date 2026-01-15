/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadCSS, loadJS } from "@web/core/assets";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component, onMounted, onWillStart, useRef, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";


export class AssetMapView extends Component {
    static template = "silver_geo.AssetMapView";
    static props = {
        ...standardFieldProps,
        nodeId: {type: [Number, String], optional: true},
        action: {optional: true},
        actionId: {optional: true},
        className: {optional: true},
        name: {optional: true},
        record: {optional: true},
        updateActionState: {optional: true}
    };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.mapRef = useRef("asset_map");
        this.filterContainerRef = useRef("model_filter_container");
        this.coordinateInputRef = useRef("coordinateInput");

        this.state = useState({
            allAssets: [],
            filteredAssets: [],
            assetModels: [],
            selectedModels: {},
        });

        onWillStart(async () => {
            await this._loadLeaflet();
        });

        onMounted(() => {
            this._initMap();
            this._loadAssets(this.props.nodeId);
        });
    }

    async _loadLeaflet() {
        await loadCSS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css");
        await loadJS("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js");
    }

    _initMap() {
        this.map = L.map(this.mapRef.el).setView([10.4806, -66.9036], 12); // Caracas

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        this.featureGroup = L.featureGroup().addTo(this.map);

        this.map.on("moveend", () => this._updateFeatureVisibility());

        this.map.on("click", (e) => {
            // This is a general map click, not on a feature
            const {lat, lng} = e.latlng;
            this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: "silver.box",
                views: [[false, "form"]],
                target: "new",
                context: {
                    default_gps_lat: lat,
                    default_gps_lon: lng,
                },
            });
        });
    }

    async _loadAssets(nodeId) {
        const response = await rpc("/silver_geo/get_assets", {node_id: nodeId});
        let rawAssets = response.assets || response || [];
        const assets = rawAssets.filter(asset =>
            asset && typeof asset === 'object' && asset.model && asset.name
        );
        const centerOn = response.center_on;

        if (centerOn) {
            this.map.setView([centerOn.lat, centerOn.lon], 16);
        }

        this.state.allAssets = assets;
        this.state.filteredAssets = [...assets];
        const models = [...new Set(assets.map(asset => asset.model))];
        this.state.assetModels = models;
        models.forEach(model => {
            this.state.selectedModels[model] = true;
        });
        this._renderFeatures();
    }

    _renderFeatures() {
        this.featureGroup.clearLayers();
        this.state.filteredAssets.forEach(asset => {
            let layer;
            if (asset.model === 'cable' && asset.line_string_wkt) {
                // Assuming line_string_wkt is a string of "lon1 lat1, lon2 lat2, ..."
                const latLngs = asset.line_string_wkt.split(',').map(pair => {
                    const [lon, lat] = pair.trim().split(' ').map(Number);
                    return [lat, lon];
                });
                const color = asset.color || '#ff0000';
                layer = L.polyline(latLngs, {color: color});
            } else if (asset.longitude && asset.latitude) {
                const icon = this._getFeatureStyle(asset);
                layer = L.marker([asset.latitude, asset.longitude], {icon: icon});
            }

            if (layer) {
                layer.asset = asset;
                layer.bindPopup(`<b>${asset.name}</b><br>Type: ${asset.model}`);
                layer.on('click', (e) => {
                    // Stop propagation to prevent map click event
                    L.DomEvent.stopPropagation(e);
                });
                this.featureGroup.addLayer(layer);
            }
        });
        this._updateFeatureVisibility();
    }

    _getFeatureStyle(asset) {
        var model = asset.model.replaceAll(".", "").replaceAll("silver", "");
        const iconPath = `/silver_geo/static/src/img/map_icons/${model}.png`;
        return L.icon({
            iconUrl: iconPath,
            iconSize: [25, 25],
            iconAnchor: [12, 12],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
    }

    _updateFeatureVisibility() {
        return;

        const zoom = this.map.getZoom();
        this.featureGroup.eachLayer(layer => {
            const asset = layer.asset;
            if (asset) {
                let isVisible = true;
                if (asset.model === 'post') {
                    isVisible = zoom >= 15;
                } else if (asset.model === 'box') {
                    isVisible = zoom > 13;
                }

                if (isVisible) {
                    if (!this.map.hasLayer(layer)) {
                        this.featureGroup.addLayer(layer);
                    }
                } else {
                    if (this.map.hasLayer(layer)) {
                        this.featureGroup.removeLayer(layer);
                    }
                }
            }
        });
    }

    onFilterChange(e) {
        const {value, checked} = e.target;
        if (value === "all") {
            for (const model in this.state.selectedModels) {
                this.state.selectedModels[model] = checked;
            }
        } else {
            this.state.selectedModels[value] = checked;
        }
        this._applyFilters();
    }

    _applyFilters() {
        const selected = Object.entries(this.state.selectedModels)
            .filter(([, isSelected]) => isSelected)
            .map(([model]) => model);
        this.state.filteredAssets = this.state.allAssets.filter(asset => selected.includes(asset.model));
        this._renderFeatures();
    }

    get allFiltersChecked() {
        return this.state.assetModels.every(model => this.state.selectedModels[model]);
    }

    onLocateCoordinates() {
        const coordsString = this.coordinateInputRef.el.value;
        const coords = coordsString.split(',').map(c => parseFloat(c.trim()));
        if (coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
            const [latitude, longitude] = coords;
            this.map.setView([latitude, longitude], 18);
            L.marker([latitude, longitude]).addTo(this.featureGroup);
            L.circle([latitude, longitude], {radius: 100}).addTo(this.featureGroup);
        } else {
            alert("Invalid coordinate format. Please use 'latitude, longitude'.");
        }
    }



}

registry.category("actions").add("silver_geo.map_view", AssetMapView);
