/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadCSS, loadJS } from "@web/core/assets";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component, onMounted, onWillStart, useRef, useState } from "@odoo/owl";

export class AssetMapView extends Component {
    static template = "silver_isp.AssetMapView";
    static props = {
        
        ...standardFieldProps,
        
        nodeId: { type: [Number, String], optional: true },

                action: {
            optional: true,
        },
                        actionId: {
            optional: true,
        },
        className: {
            optional: true,
        },
        name: {
            optional: true,
        },
        record: {
            optional: true
        }

    };

    setup() {
        this.rpc = useService("rpc");
        this.orm = useService("orm");

        this.mapRef = useRef("asset_map");
        this.popupRef = useRef("popup");
        this.popupContentRef = useRef("popup_content");
        this.popupCloserRef = useRef("popup_closer");
        this.filterContainerRef = useRef("model_filter_container");

        this.state = useState({
            allAssets: [],
            filteredAssets: [],
            assetModels: [],
            selectedModels: {},
        });

        onWillStart(async () => {
            await this._loadOpenLayers();
        });

        onMounted(() => {
            console.log(["nodemid", this.props.nodeId]);
            this._initMap();
            this._loadAssets(this.props.nodeId);
        });
    }

    async _loadOpenLayers() {
        await loadCSS("https://cdn.jsdelivr.net/npm/ol@v10.6.0/ol.css");
        await loadJS("https://cdn.jsdelivr.net/npm/ol@v10.6.0/dist/ol.js");
    }

    _initMap() {
        const container = this.popupRef.el;
        const content = this.popupContentRef.el;
        const closer = this.popupCloserRef.el;

        this.overlay = new ol.Overlay({
            element: container,
            autoPan: {
                animation: {
                    duration: 250,
                },
            },
        });

        closer.onclick = () => {
            this.overlay.setPosition(undefined);
            closer.blur();
            return false;
        };

        this.map = new ol.Map({
            target: this.mapRef.el,
            layers: [
                new ol.layer.Tile({
                    source: new ol.source.OSM(),
                }),
            ],
            view: new ol.View({
                center: ol.proj.fromLonLat([-66.9036, 10.4806]), // Caracas
                zoom: 12,
            }),
            overlays: [this.overlay],
        });

        this.vectorSource = new ol.source.Vector();
        const vectorLayer = new ol.layer.Vector({
            source: this.vectorSource,
        });
        this.map.addLayer(vectorLayer);

        this.map.on("singleclick", (evt) => {
            const feature = this.map.forEachFeatureAtPixel(evt.pixel, (f) => f);
            if (feature) {
                const coordinates = feature.getGeometry().getCoordinates();
                const asset = feature.get("asset");
                content.innerHTML = `<b>${asset.name}</b><br>Type: ${asset.model}`;
                this.overlay.setPosition(coordinates);
            } else {
                this.overlay.setPosition(undefined);
            }
        });
    }

    async _loadAssets(nodeId) {
        const response = await this.rpc(
            "/silver_isp/get_assets",
            { node_id: nodeId }
        );

        let rawAssets = response.assets || response || [];
        
        // Filtra cualquier asset que no sea un objeto válido o no tenga las propiedades mínimas.
        const assets = rawAssets.filter(asset => 
            asset && typeof asset === 'object' && asset.model && asset.name
        );

        const centerOn = response.center_on;

        if (centerOn) {
            this.map.getView().setCenter(ol.proj.fromLonLat([centerOn.lon, centerOn.lat]));
            this.map.getView().setZoom(16);
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
        this.vectorSource.clear();
        const features = this.state.filteredAssets.map(asset => {
            var model = asset.model.replaceAll(".","_");
            const iconPath = `/silver_isp/static/src/img/map_icons/${model}.svg`;
            const feature = new ol.Feature({
                geometry: new ol.geom.Point(ol.proj.fromLonLat([asset.longitude, asset.latitude])),
                asset: asset,
            });
            feature.setStyle(new ol.style.Style({
                image: new ol.style.Icon({
                    anchor: [0.5, 1],
                    src: iconPath,
                    scale: 0.5,
                    imgSize: [48, 48],
                }),
            }));
            return feature;
        });
        this.vectorSource.addFeatures(features);
    }

    onFilterChange(e) {
        const { value, checked } = e.target;
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
}

registry.category("actions").add("silver_isp.map_view", AssetMapView);
