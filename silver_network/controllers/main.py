from odoo import http
from odoo.http import request
import json
from odoo.addons.silver_network.models.silver_netdev import _format_speed


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
        netdev = request.env['silver.netdev'].browse(int(netdev_id))
        if not netdev.exists():
            return {'error': 'Device not found'}

        api = netdev._get_api_connection()
        if not api:
            return {'error': 'Connection failed'}

        try:
            # Convert string of names to list
            if isinstance(interface_names, str):
                interface_names = interface_names.split(',')

            traffic_data = api.path('/interface/monitor-traffic')({
                'numbers': ",".join(interface_names),
                'once': ''
            })
            
            stats = {}
            for item in traffic_data:
                stats[item['name']] = {
                    'rx_speed': _format_speed(item.get('rx-bits-per-second', 0)),
                    'tx_speed': _format_speed(item.get('tx-bits-per-second', 0)),
                }
            return stats
        except Exception as e:
            return {'error': str(e)}
        finally:
            if api:
                api.close()
