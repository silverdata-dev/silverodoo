from odoo import http
from odoo.http import request
import json


class AssetMapController(http.Controller):

    @http.route('/silver_geo/map_view', type='http', auth='user')
    def show_map(self, node_id=None, **kw):
        return request.render('silver_geo.map_view_template', {'node_id': node_id})

    @http.route('/silver_geo/get_assets', type='json', auth='user')
    def get_assets(self, node_id=None, **kw):
        asset_models = {
            'silver.node': [('id', '=', int(node_id))] if node_id else [],
            'silver.box': [('node_id', '=', int(node_id))] if node_id else [],
            'silver.core': [('node_id', '=', int(node_id))] if node_id else [],
            'silver.olt': [('node_id', '=', int(node_id))] if node_id else [],
            'silver.ap': [('node_id', '=', int(node_id))] if node_id else [],
        }

        all_assets = []
        center_coords = None

        for model_name, domain in asset_models.items():
            if model_name not in request.env:
                continue
            
            # Asegurarse de que solo se buscan registros con una dirección y coordenadas válidas
            full_domain = domain + [('silver_address_id', '!=', False), ('silver_address_id.latitude', '!=', 0), ('silver_address_id.longitude', '!=', 0)]
            
            records = request.env[model_name].search(full_domain)
            print((" records" , records, model_name, full_domain))

            for record in records:
                all_assets.append({
                    'id': record.id,
                    'name': record.name,
                    'model': model_name,
                    'latitude': record.silver_address_id.latitude,
                    'longitude': record.silver_address_id.longitude,
                })

        # Centrar el mapa en el nodo principal si se proporciona
        if node_id:
            try:
                node = request.env['silver.node'].browse(int(node_id))
                if node.exists() and node.silver_address_id:
                    center_coords = {
                        'lat': node.silver_address_id.latitude,
                        'lon': node.silver_address_id.longitude
                    }
            except (ValueError, TypeError):
                pass  # Ignorar si el node_id no es válido

        return {
            'assets': all_assets,
            'center_on': center_coords
        }
