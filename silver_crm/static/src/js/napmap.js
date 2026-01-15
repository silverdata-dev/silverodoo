/** @odoo-module **/

import { registry } from "@web/core/registry";
import { AssetMapView } from "@silver_geo/js/map_view";
import { onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class NapMapSelectorView extends AssetMapView {
    static template = "NapMapSelectorView";

    setup() {
        super.setup(); // Llamar al setup de la clase padre
        //this.rpc = useService("rpc");

        // Leer los parámetros del contexto de la acción
        const context = this.props.action.context;
        this.nodeId = context.node_id;
        this.customerLat = context.customer_lat;
        this.customerLon = context.customer_lon;
        this.leadId = context.lead_id;

        onMounted(() => {
            this._initMap();
            this._loadAssets();
        });
    }

    // Sobrescribir _loadAssets para usar el nodeId del contexto
    async _loadAssets() {
        // Llamar al nuevo controlador que filtra por nodo
        const response = await rpc(
            "/silver_crm/get_nap_boxes",
            { node_id: this.nodeId }
        );

        let rawAssets = response.assets || [];
        const assets = rawAssets.filter(asset =>
            asset && typeof asset === 'object' && asset.model && asset.name
        );

        this.state.allAssets = assets;
        this.state.filteredAssets = [...assets];
        const models = [...new Set(assets.map(asset => asset.model))];
        this.state.assetModels = models;
        console.log(["aassets", assets, models]);
        models.forEach(model => {
            this.state.selectedModels[model] = true;
        });



     /*   for (const asset of assets) {
                 var model = asset.model.replaceAll(".", "_");
                 console.log(["as", model, asset.name]);
            if (asset.latitude && asset.longitude && ['box', 'node'].includes(model)) {
                const icon = ol.icon({iconUrl:`/silver_geo/static/src/img/map_icons/${model}.png`,  iconSize: [25, 41], iconAnchor: [12, 41] });
                //const icon = icons[asset.model] || icons.default;
                ol.marker([asset.latitude, asset.longitude], { icon: icon, opacity: 0.7 })
                    .bindPopup(`<b>${asset.model.toUpperCase()}:</b><br/>${asset.name}`)
                    .addTo(this.map);
            }
        }*/

        this._renderFeatures();
    }

    // Sobrescribir _initMap para añadir el marcador del cliente y manejar la selección
    _initMap() {
        super._initMap(); // Ejecutar la inicialización del mapa base

        // Centrar el mapa en la ubicación del cliente
        if (this.customerLat && this.customerLon) {
            const customerCoords = ol.proj.fromLonLat([this.customerLon, this.customerLat]);
            this.map.getView().setCenter(customerCoords);
            this.map.getView().setZoom(18); // Un zoom más cercano

            // Añadir un marcador para el cliente
            const customerMarker = new ol.Feature({
                geometry: new ol.geom.Point(customerCoords),
            });
            customerMarker.setStyle(new ol.style.Style({
                image: new ol.style.Icon({
                    anchor: [0.5, 1],
                    //src:`/silver_geo/static/src/img/map_icons/${model}.png`
                    src: '/silver_crm/static/src/img/map_icons/marker-shadow.png', // Un ícono distintivo
                    scale: 0.5,
                }),
            }));
            this.vectorSource.addFeature(customerMarker);
        }

        // Configurar el manejador de clics para la selección de cajas NAP
        this.map.on("singleclick", (evt) => {
            const feature = this.map.forEachFeatureAtPixel(evt.pixel, (f) => f);
            if (feature) {
                const asset = feature.get("asset");
                if (asset && asset.model === 'box') { // Solo reaccionar a clics en cajas NAP
                    const coordinates = feature.getGeometry().getCoordinates();

                    // Crear el contenido del popup con el botón "Seleccionar"
                    const popupContent = `
                        <b>${asset.name}</b><br>
                        <button class="btn btn-primary btn-sm mt-2" id="select-nap-button">
                            Seleccionar esta Caja
                        </button>
                    `;
                    this.popupContentRef.el.innerHTML = popupContent;
                    this.overlay.setPosition(coordinates);

                    // Añadir el listener al botón recién creado
                    document.getElementById('select-nap-button').addEventListener('click', () => {
                        this._selectNapBox(asset.id);
                    });
                }
            } else {
                this.overlay.setPosition(undefined); // Ocultar popup si se hace clic fuera
            }
        });
    }

    _renderFeatures() {
        this.vectorSource.clear(); // Limpiar marcadores existentes, excepto el del cliente

        // Volver a añadir el marcador del cliente si existe
        if (this.customerLat && this.customerLon) {
            const customerCoords = ol.proj.fromLonLat([this.customerLon, this.customerLat]);
            const customerMarker = new ol.Feature({
                geometry: new ol.geom.Point(customerCoords),
            });
            customerMarker.setStyle(new ol.style.Style({
                image: new ol.style.Icon({
                    anchor: [0.5, 1],
                    src: '/silver_geo/static/src/img/map_icons/node.png',
                    scale: 0.5,
                }),
            }));
            this.vectorSource.addFeature(customerMarker);
        }


        const features = this.state.filteredAssets.map(asset => {
            let feature;
            // Usar asset.lon y asset.lat en lugar de asset.longitude y asset.latitude
            if (asset.longitude && asset.latitude) {
                feature = new ol.Feature({
                    geometry: new ol.geom.Point(ol.proj.fromLonLat([asset.longitude, asset.latitude])),
                });
                const style = this._getFeatureStyle(asset);
                console.log(["filtered", asset, style]);
                feature.setStyle(style);
                feature.set('asset', asset);
                feature.set('originalStyle', style);
            }
            return feature;
        }).filter(Boolean); // Filtrar nulos si alguna caja no tuviera coordenadas


        console.log(['filtered', this.state.filteredAssets, this.state.allAssets, features]);

        this.vectorSource.addFeatures(features);
        this._updateFeatureVisibility(); // Aplicar visibilidad inicial
    }

    async _selectNapBox(boxId) {
        // Llamar al método de Python en silver.box para asignar la caja al lead
        await rpc({
            model: 'silver.box',
            method: 'action_select_nap_and_assign_to_lead',
            args: [boxId, this.leadId],
        });

        // Cerrar la vista de mapa y volver a la oportunidad
        this.actionService.doAction({ type: 'ir.actions.act_window_close' });
    }
}

// Registrar la nueva acción de cliente
registry.category("actions").add("silver_crm.nap_map_selector", NapMapSelectorView);
