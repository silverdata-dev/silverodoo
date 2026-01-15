/** @odoo-module **/

import { registry } from "@web/core/registry";
import { AssetMapView } from "@silver_geo/js/map_view";
import { onMounted } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

export class NapMapSelectorView extends AssetMapView {
    static template = "NapMapSelectorView";

    setup() {
        super.setup();
        const context = this.props.action.context;
        this.nodeId = context.node_id;
        this.customerLat = context.customer_lat;
        this.customerLon = context.customer_lon;
        this.leadId = context.lead_id;

        onMounted(() => {
            // _initMap is called by parent, but we might need to adjust view after assets are loaded.
            this._loadAssets();
        });
    }

    async _loadAssets() {
        const response = await rpc("/silver_crm/get_nap_boxes", { node_id: this.nodeId });
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

        // Center map on customer after assets are loaded and rendered
        if (this.customerLat && this.customerLon) {
            this.map.setView([this.customerLat, this.customerLon], 18);
        }
    }

    _initMap() {
        super._initMap();
        // The map is now initialized in the parent class using Leaflet.
        // We can add customer-specific markers or layers here.
        if (this.customerLat && this.customerLon) {
            L.marker([this.customerLat, this.customerLon], {
                icon: L.icon({
                    iconUrl: '/silver_crm/static/src/img/map_icons/marker-shadow.png',
                    iconSize: [41, 41],
                    iconAnchor: [12, 41],
                })
            }).addTo(this.map).bindPopup("Customer Location");
        }

        const context = this.props.action.context;
        const addressLat = context.address_lat;
        const addressLon = context.address_lon;
     const leadName = context.lead_name;

        if (addressLat && addressLon) {
            const circle = L.circle([addressLat, addressLon], {
                color: 'blue',
                fillColor: '#0000ff',
                fillOpacity: 0.2,
                radius: 100
            }).addTo(this.map);
            circle.bindPopup(`<b>${leadName}</b>`).openPopup();
        }
    }

    _renderFeatures() {
        super._renderFeatures(); // This will clear layers and render assets from filteredAssets

        // Now, add specific popups for NAP boxes
        this.featureGroup.eachLayer(layer => {
            const asset = layer.asset;
            if (asset && asset.model === 'box') {
                const popupContent = this._createPopupContent(asset);
                layer.bindPopup(popupContent);

                layer.on('popupopen', () => {
                    const button = document.getElementById(`select-nap-button-${asset.id}`);
                    if (button) {
                        button.onclick = () => {
                            this._selectNapBox(asset.id);
                        };
                    }
                });
            }
        });
    }

    _createPopupContent(asset) {
        // Note: We need a unique ID for the button to avoid conflicts
        return `
            <b>${asset.name}</b><br>
            <button class="btn btn-primary btn-sm mt-2" id="select-nap-button-${asset.id}">
                Seleccionar esta Caja
            </button>
        `;
    }

    async _selectNapBox(boxId) {
        await rpc('/silver_crm/select_nap_box', {
            box_id: boxId,
            lead_id: this.leadId,
        });
        this.actionService.doAction({ type: 'ir.actions.act_window_close' });
    }
}

registry.category("actions").add("silver_crm.nap_map_selector", NapMapSelectorView);
