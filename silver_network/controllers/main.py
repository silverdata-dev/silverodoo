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
