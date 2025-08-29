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
        this.actionService = useService("action");

        this.mapRef = useRef("asset_map");
        this.popupRef = useRef("popup");
        this.popupContentRef = useRef("popup_content");
        this.popupCloserRef = useRef("popup_closer");
        this.filterContainerRef = useRef("model_filter_container");
        this.coordinateInputRef = useRef("coordinateInput");

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

        this.map.on("moveend", () => this._updateFeatureVisibility());

        this.map.on("singleclick", (evt) => {
            const feature = this.map.forEachFeatureAtPixel(evt.pixel, (f) => f);
            if (feature) {
                const coordinates = feature.getGeometry().getCoordinates();
                const asset = feature.get("asset");
                if (!asset) {
                                    this.overlay.setPosition(undefined);
                const coordinates = ol.proj.transform(evt.coordinate, 'EPSG:3857', 'EPSG:4326');
                this.actionService.doAction({
                    type: "ir.actions.act_window",
                    res_model: "isp.box",
                    views: [[false, "form"]],
                    target: "new",
                    context: {
                        default_gps_lat: coordinates[1],
                        default_gps_lon: coordinates[0],
                    },
                });
                } else {
                                    content.innerHTML = `<b>${asset.name}</b><br>Type: ${asset.model}`;
                this.overlay.setPosition(coordinates);

                }
            } else {

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
        console.log(["assets", assets, models]);
        models.forEach(model => {
            this.state.selectedModels[model] = true;
        });
        this._renderFeatures();
    }

    _renderFeatures() {
        this.vectorSource.clear();
        const features = this.state.filteredAssets.map(asset => {
            let feature;
            let style;
            if (asset.model === 'cable' && asset.line_string_wkt) {
                const wkt = new ol.format.WKT();
                feature = wkt.readFeature('LINESTRING('+asset.line_string_wkt+')', {
                    dataProjection: 'EPSG:4326',
                    featureProjection: 'EPSG:3857'
                });

                const color = asset.color; // #RRGGBBAA
                const a = parseInt(color.slice(1, 3), 16);
                const r = parseInt(color.slice(3, 5), 16);
                const g = parseInt(color.slice(5, 7), 16);
                const b = parseInt(color.slice(7, 9), 16) / 255;

                console.log(['color', color, r, g, b, a])

                style = new ol.style.Style({
                    stroke: new ol.style.Stroke({
                        color: `rgba(${r}, ${g}, ${b}, ${a})`,
                        width: 3
                    })
                });
            } else if (asset.longitude && asset.latitude) {
                feature = new ol.Feature({
                    geometry: new ol.geom.Point(ol.proj.fromLonLat([asset.longitude, asset.latitude])),
                });
                style = this._getFeatureStyle(asset);
            }

            if (feature) {
                feature.set('asset', asset);
                feature.setStyle(style);
                feature.set('originalStyle', style); // Store original style
                return feature;
            }
            return null;
        }).filter(Boolean);

        this.vectorSource.addFeatures(features);
        this._updateFeatureVisibility(); // Set initial visibility
    }

    _getFeatureStyle(asset) {
        var model = asset.model.replaceAll(".", "_");
        const iconPath = `/silver_isp/static/src/img/map_icons/${model}.png`;
        return new ol.style.Style({
            image: new ol.style.Icon({
                anchor: [0.5, 1],
                src: iconPath,
                scale: 0.3,
                imgSize: [48, 48],
            }),
        });
    }

    _updateFeatureVisibility() {
        const zoom = this.map.getView().getZoom();
        console.log(["update",  this.map.getView().getZoom()]);
        this.vectorSource.getFeatures().forEach(feature => {
            const asset = feature.get("asset");
            if (asset) {
                let isVisible = true;
                if (asset.model === 'post') {
                    isVisible = zoom >= 15;
                } else if (asset.model === 'cto') {
                    isVisible = zoom > 13;
                }
                
                feature.setStyle(isVisible ? feature.get('originalStyle') : new ol.style.Style({}));
            }
        });
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

    onLocateCoordinates() {
       const coordsString = this.coordinateInputRef.el.value;
        let coords = [];

        // Regex para encontrar coordenadas en el formato "latitud,longitud"
        // El patrón busca un número decimal opcionalmente negativo, seguido de una coma,
        // y otro número decimal opcionalmente negativo.
        const regex = /-?\d+\.?\d*,\s*-?\d+\.?\d*/;
        const match = coordsString.match(regex);

        if (match) {
          // Si se encuentra un patrón de coordenadas en la URL, las extraemos.
          coords = match[0].split(',').map(c => parseFloat(c.trim()));
        } else {
          // Si no hay un patrón de coordenadas, asumimos que el string completo
          // es el par de coordenadas.
          coords = coordsString.split(',').map(c => parseFloat(c.trim()));
        }


        if (coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
            const longitude = coords[1];
            const latitude = coords[0];
            const centerCoordinates = ol.proj.fromLonLat([longitude, latitude]);

            // Center map
            this.map.getView().setCenter(centerCoordinates);
            this.map.getView().setZoom(18);

            // Add a generic icon
            const iconFeature = new ol.Feature({
                geometry: new ol.geom.Point(centerCoordinates),
            });

            const iconStyle = new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 10,
                    fill: new ol.style.Fill({
                        color: 'red'
                    }),
                    stroke: new ol.style.Stroke({
                        color: 'white', 
                        width: 2
                    })
                })
            });
            iconFeature.setStyle(iconStyle);
            this.vectorSource.addFeature(iconFeature);

            // Add a circle around the icon
            const circleFeature = new ol.Feature({
                geometry: new ol.geom.Circle(centerCoordinates, 100),
            });

            const circleStyle = new ol.style.Style({
                fill: new ol.style.Fill({
                    color: 'rgba(255, 0, 0, 0.1)'
                }),
                stroke: new ol.style.Stroke({
                    color: 'red',
                    width: 1
                })
            });
            circleFeature.setStyle(circleStyle);
            this.vectorSource.addFeature(circleFeature);


        } else {
            alert("Invalid coordinate format. Please use 'latitude, longitude'.");
        }
    }
}

registry.category("actions").add("silver_isp.map_view", AssetMapView);
