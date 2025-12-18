from odoo import http
from odoo.http import request
import json



def _format_speed(bits_per_second):
    bits_per_second = int(bits_per_second)
    if bits_per_second < 1000:
        return f"{bits_per_second} B/s"
    elif bits_per_second < 1000000:
        return f"{bits_per_second / 1000:.2f} KB/s"
    elif bits_per_second < 1000000000:
        return f"{bits_per_second / 1000000:.2f} MB/s"
    else:
        return f"{bits_per_second / 1000000000:.2f} GB/s"



class SystemStatsController(http.Controller):

    @http.route('/silver_network/get_system_stats', type='jsonrpc', auth='user')
    def get_system_stats(self, netdev_id, **kw):
        try:
            print(("netdev", netdev_id))
            netdev = request.env['silver.core'].browse(int(netdev_id))
            #netdev = request.env['silver.core'].search([("id",'=', netdev_id)]) #int(netdev_id))
            if not netdev.exists():
                return {'error': 'Device not found'}

            api, e = netdev._get_api_connection()
            if not api:
                return {'error': f'Connection failed: {e}'}

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

    @http.route('/silver_network/get_interface_stats', type='jsonrpc', auth='user')
    def get_interface_stats(self, netdev_id, interface_names, **kw):
        netdev = request.env['silver.core'].browse(int(netdev_id))
        print(("netdev", netdev_id))
        #netdev = request.env['silver.core'].search([("id", '=', netdev_id)] ) # int(netdev_id))
        if not netdev.exists():
            return {'error': 'Device not found'}

        api,e = netdev._get_api_connection()
        if not api:
            return {'error': f'Connection failed: {e}'}

        try:
        #if 1:
            # Convert string of names to list
            if isinstance(interface_names, str):
                interface_names = interface_names.split(',')

            stats = {}
            traffic_map = {}

            chunk_size = 90  # A safe limit below 100
            for i in range(0, len(interface_names), chunk_size):
                chunk = interface_names[i:i + chunk_size]
                print(("chunk", ",".join(chunk)))
                traffic_chunk_data = api.path('/interface')('monitor-traffic', interface=",".join(chunk), once='')
                for item in traffic_chunk_data:
                    traffic_map[item['name']] = item

            #print(("chunk", chunk, traffic_chunk_data, traffic_map))

            for name in interface_names:
            #    name = interface.get('name')
                item = traffic_map.get(name, {})

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
