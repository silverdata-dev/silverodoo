# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ContractTrafficWizard(models.TransientModel):
    _name = 'silver.contract.traffic.wizard'
    _description = 'Wizard to display real-time traffic for a contract'

    core_id = fields.Many2one('silver.core', string='Core Router', required=True)
    interface = fields.Char(string='Interface', required=True)
    
    # Reusing fields for chart display
    rate_up = fields.Char(string='Upload', readonly=True, default='0 kbps')
    rate_down = fields.Char(string='Download', readonly=True, default='0 kbps')
    speed_chart = fields.Text(readonly=True)

    def _format_speed(self, bits_per_second):
        if not isinstance(bits_per_second, (int, float)):
            return "0 bps"
        if bits_per_second > 1000000:
            return f"{bits_per_second / 1000000:.2f} Mbps"
        if bits_per_second > 1000:
            return f"{bits_per_second / 1000:.2f} kbps"
        return f"{bits_per_second} bps"

    @api.model
    def get_interface_speed(self, wizard_id):
        wizard = self.browse(wizard_id)
        if not wizard or not wizard.core_id:
            return {'upload': 0, 'download': 0}

        api = None
        try:
            api,e = wizard.core_id._get_api_connection()
            if not api:
                print((f"error core:{e}"))
                return {'upload': 0, 'download': 0}

            interface_path = api.path('/interface')
            traffic_generator = interface_path('monitor-traffic', interface=wizard.interface, once=True)
            traffic = next(traffic_generator, None)

            if traffic:
                tx_speed = traffic.get('tx-bits-per-second', 0)
                rx_speed = traffic.get('rx-bits-per-second', 0)
                return {'upload': tx_speed, 'download': rx_speed}
            
            return {'upload': 0, 'download': 0}
        except Exception:
            return {'upload': 0, 'download': 0}
        finally:
            if api:
                api.close()
