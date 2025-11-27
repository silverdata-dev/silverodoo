/** @odoo-module **/

import { registry } from "@web/core/registry";
import { AssetMapView } from "@silver_geo/js/map_view"; // Importar la clase base

export class NapMapSelectorView extends AssetMapView {
    static template = "NapMapSelectorView";

    setup() {
        super.setup(); // Llamar al setup de la clase padre

        // Leer los parámetros del contexto de la acción
        const context = this.props.action.context;
        this.nodeId = context.node_id;
        this.customerLat = context.customer_lat;
        this.customerLon = context.customer_lon;
        this.leadId = context.lead_id;
    }

    // Sobrescribir _loadAssets para usar el nodeId del contexto
    async _loadAssets() {
        // Llamar al nuevo controlador que filtra por nodo
        const response = await this.rpc(
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
        models.forEach(model => {
            this.state.selectedModels[model] = true;
        });
        this._renderFeatures();
    }

    // Sobrescribir _initMap para añadir el marcador del cliente
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
                    src: '/silver_crm/static/src/img/customer_marker.png', // Un ícono distintivo
                    scale: 0.5,
                }),
            }));
            this.vectorSource.addFeature(customerMarker);
        }
    }

    // Sobrescribir el manejador de clics para la selección
    _initMap() {
        // ... (código de inicialización del mapa base de la clase padre) ...

        this.map.on("singleclick", (evt) => {
            const feature = this.map.forEachFeatureAtPixel(evt.pixel, (f) => f);
            if (feature) {
                const asset = feature.get("asset");
                if (asset && asset.model === 'nap') { // Solo reaccionar a clics en cajas NAP
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

    async _selectNapBox(boxId) {
        // Llamar al método de Python en silver.box para asignar la caja al lead
        await this.rpc({
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
