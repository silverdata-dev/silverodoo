/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useRef, onWillUnmount } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class SilverMapWidget extends Component {
    static template = "silver_base.SilverMapWidget";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.mapContainer = useRef("mapContainer");
        this.orm = useService("orm");
        this.map = null;

        onMounted(() => {
            this.initializeMap();
        });

        onWillUnmount(() => {
            if (this.map) {
                this.map.remove();
            }
        });
    }

    async initializeMap() {
        if (!this.mapContainer.el) return;

        // 1. Coordenadas iniciales (desde el registro o default Venezuela)
        const lat = this.props.record.data.latitude || 10.4806;
        const lng = this.props.record.data.longitude || -66.9036;

        // 2. Iniciar Leaflet
        // Check if L is defined (Leaflet loaded)
        if (typeof L === 'undefined') {
            console.error("Leaflet is not loaded.");
            return;
        }

        this.map = L.map(this.mapContainer.el).setView([lat, lng], 15);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; OpenStreetMap contributors',
        }).addTo(this.map);

        // Marcador inicial
        this.marker = L.marker([lat, lng], { draggable: true }).addTo(this.map);

        // 3. Configurar el Buscador (Leaflet Geosearch)
        if (typeof window.GeoSearch !== 'undefined') {
            const provider = new window.GeoSearch.OpenStreetMapProvider();

            const searchControl = new window.GeoSearch.GeoSearchControl({
                provider: provider,
                style: 'bar',
                autoComplete: true,
                autoCompleteDelay: 250,
                showMarker: false, // Usaremos nuestro propio marcador
                retainZoomLevel: false,
                animateZoom: true,
                keepResult: true,
                searchLabel: 'Buscar calle, edificio, zona...',
            });

            this.map.addControl(searchControl);

            // 4. EVENTO: Cuando el usuario selecciona una dirección en el buscador
            this.map.on('geosearch/showlocation', async (result) => {
                const location = result.location;

                console.log(("showlocation", location));

                // Mover el marcador
                this.marker.setLatLng([location.y, location.x]);
                
                // ACTUALIZACIÓN: Llamar al backend para reverse geocoding robusto
                await this.updateOdooFields(location.y, location.x);
            });
        }

        // Evento: Al mover el marcador manualmente
        this.marker.on('dragend', async (event) => {

            const position = event.target.getLatLng();
            console.log(["dragend", position]);
            // También llamamos al backend al arrastrar, para actualizar la dirección
            await this.updateOdooFields(position.lat, position.lng);
        });
        
        // Force map resize to ensure tiles load correctly if container size changes
        setTimeout(() => {
            this.map.invalidateSize();
        }, 100);
    }

    async updateOdooFields(lat, lng) {
        // En lugar de usar los datos crudos del JS, llamamos al servidor
        try {
            const result = await this.orm.call("silver.address", "get_address_from_coords", [lat, lng]);
            
            const updates = {
                latitude: lat,
                longitude: lng,
            };


            // Mezclamos lo que devolvió Python
            if (result.street) updates.street = result.street;
            if (result.house_number) updates.house_number = result.house_number;
            if (result.zip) updates.zip = result.zip;
            if (result.building) updates.building = result.building;
            
            // Relacionales
            if (result.country_id) updates.country_id = result.country_id;
            if (result.state_id) updates.state_id = result.state_id;
            if (result.zone_id) updates.zone_id = result.zone_id;


             console.log(["updateOdooFields", lat, lng, result, updates]);

            // Aplicar cambios
            await this.props.record.update(updates);
            
        } catch (error) {
            console.error("Error al obtener detalles de dirección desde el servidor:", error);
            // Fallback: solo coordenadas
            await this.props.record.update({
                latitude: lat,
                longitude: lng,
            });
        }
    }
}

export const silverMapWidget = {
    component: SilverMapWidget,
    fieldDependencies: [
        { name: "latitude", type: "float" },
        { name: "longitude", type: "float" },
        { name: "lat_long_display", type: "char" }, // Nuevo: Campo combinado de lat/lon
        { name: "street", type: "char" },
        { name: "street2", type: "char" },
        { name: "building", type: "char" },
        { name: "floor", type: "char" }, // Añadido para el piso
        { name: "house_number", type: "char" },
        { name: "zip", type: "char" },
        { name: "state_id", type: "many2one" },
        { name: "country_id", type: "many2one" },
//        { name: "municipality_id", type: "many2one" }, // Added
//        { name: "parish_id", type: "many2one" }, // Added
        { name: "zone_id", type: "many2one" },
    ],
};

registry.category("fields").add("silver_address_map", silverMapWidget);