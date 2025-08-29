
from odoo import http
from odoo.http import request
import json

class AssetMapController(http.Controller):


    @http.route('/silver_isp/map_view', type='http', auth='user')
    def show_map(self, node_id=None, **kw):
        return request.render('silver_isp.map_view_template', {'node_id': node_id})

    @http.route('/silver_isp/get_assets', type='json', auth='user')
    def get_assets(self, node_id=None, **kw):
        # Lista de modelos que heredan de 'isp.asset' y tienen coordenadas
        asset_models = [
            'isp.node', 'isp.box', 'isp.splice_closure', 'isp.core',
            'isp.splitter', 'isp.olt', 'isp.ap'
        ]
        
        
        root_id = None
        # Si se proporciona un node_id, busca sus coordenadas para centrar el mapa
        if node_id:
            try:
                node = request.env['isp.node'].browse(int(node_id))
                if node.exists() and node.gps_lat and node.gps_lon:
                    center_coords = {'lat': node.gps_lat, 'lon': node.gps_lon}
                    root_id = node.asset_id.id
            except (ValueError, TypeError):
                pass  # Ignorar si el node_id no es válido
        all_assets = []
        center_coords = None

        print(("get_assets", node_id, root_id))

        #"""



        domain = ['|', '|', ('line_string_wkt', '!=', ''), ('gps_lat', '!=', 0), ('gps_lon', '!=', 0)]
        if root_id:
            domain.extend(['|','|',('parent_id', '=', root_id), ('root_id', '=', root_id), ('id', '=', root_id)])

        assets = request.env["isp.asset"].search(domain)

        count={}
            
        for asset in assets:
                count[asset.asset_type] = count.get(asset.asset_type, 0)+1
                if (asset.line_string_wkt):
                    all_assets.append({
                    'id': asset.id,
                    'name': asset.name,
                    'model': asset.asset_type,
                    'line_string_wkt': asset.line_string_wkt,
                    'color': asset.color,
                })
                else:
                    all_assets.append({
                    'id': asset.id,
                    'name': asset.name,
                    'model': asset.asset_type,
                    'latitude': asset.gps_lat,
                    'longitude': asset.gps_lon,
                })

        print(("asset", count))
        """
        for model_name in asset_models:
            if model_name not in request.env:
                continue
            
            domain = [('gps_lat', '!=', 0), ('gps_lon', '!=', 0)]
            
            # TODO: Implementar la lógica de filtrado de assets si se proporciona un node_id.
            # Ejemplo: si quieres mostrar solo el nodo actual, descomenta la siguiente línea.
            # if node_id and model_name == 'isp.node':
            #     domain.append(('id', '=', int(node_id)))

            assets = request.env[model_name].search(domain)
            
            for asset in assets:
                all_assets.append({
                    'id': asset.id,
                    'name': asset.name,
                    'model': model_name,
                    'latitude': asset.gps_lat,
                    'longitude': asset.gps_lon,
                })
                """
        return {
            'assets': all_assets,
            'center_on': center_coords
        }
