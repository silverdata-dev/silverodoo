from odoo import http
from odoo.http import request
import json

class SystemStatsController(http.Controller):

    @http.route('/silver_network/get_system_stats', type='json', auth='user')
    def get_system_stats(self, netdev_id, **kw):
        try:
            netdev = request.env['silver.netdev'].browse(int(netdev_id))
            if not netdev.exists():
                return {'error': 'Device not found'}

            api = netdev._get_api_connection()
            if not api:
                return {'error': 'Connection failed'}

            try:
                resource = tuple(api.path('/system/resource'))
                if not resource:
                    return {'error': 'Could not fetch system resource'}
                
                stats = resource[0]
                cpu_load = stats.get('cpu-load', 0)
                total_memory = stats.get('total-memory', 1)
                free_memory = stats.get('free-memory', 0)
                
                # Calculate RAM usage percentage
                ram_usage = 0
                if total_memory > 0:
                    used_memory = total_memory - free_memory
                    ram_usage = round((used_memory / total_memory) * 100)

                return {
                    'cpu_load': cpu_load,
                    'ram_usage': ram_usage,
                }
            finally:
                if api:
                    api.close()
        except Exception as e:
            return {'error': str(e)}

    @http.route('/silver_network/get_interface_stats', type='json', auth='user')
    def get_interface_stats(self, netdev_id, interface_names, **kw):
        try:
            netdev = request.env['silver.netdev'].browse(int(netdev_id))
            if not netdev.exists():
                return {'error': 'Device not found'}

            api = netdev._get_api_connection()
            if not api:
                return {'error': 'Connection failed'}

            try:
                traffic_data = api.path('/interface/monitor').call('', {
                    'numbers': ",".join(interface_names),
                    'once': ''
                })
                
                stats = {}
                for item in traffic_data:
                    stats[item['name']] = {
                        'rx_speed': request.env['silver.netdev']._format_speed(item.get('rx-bits-per-second', 0)),
                        'tx_speed': request.env['silver.netdev']._format_speed(item.get('tx-bits-per-second', 0)),
                    }
                return stats
            finally:
                if api:
                    api.close()
        except Exception as e:
            return {'error': str(e)}

class AssetMapController(http.Controller):


    @http.route('/silver_network/map_view', type='http', auth='user')
    def show_map(self, node_id=None, **kw):
        return request.render('silver_network.map_view_template', {'node_id': node_id})

    @http.route('/silver_network/get_assets', type='json', auth='user')
    def get_assets(self, node_id=None, **kw):
        # Lista de modelos que heredan de 'silver.asset' y tienen coordenadas
        asset_models = [
            'silver.node', 'silver.box', 'silver.splice_closure', 'silver.core',
            'silver.splitter', 'silver.olt', 'silver.ap'
        ]
        
        
        root_id = None
        # Si se proporciona un node_id, busca sus coordenadas para centrar el mapa
        if node_id:
            try:
                node = request.env['silver.node'].browse(int(node_id))
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

        assets = request.env["silver.asset"].search(domain)

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
            # if node_id and model_name == 'silver.node':
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
