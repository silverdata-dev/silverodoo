# -*- coding: utf-8 -*-

from odoo import models, fields, api

class IspRouterInterfaceWizard(models.Model):
    _name = 'isp.netdev.interface.wizard'
    _description = 'ISP Router Interface Wizard'

    line_ids = fields.One2many('isp.netdev.interface.wizard.line', 'wizard_id', string='Interfaces')
    router_id = fields.Many2one('isp.netdev')

class IspRouterInterfaceWizardLine(models.Model):
    _name = 'isp.netdev.interface.wizard.line'
    _description = 'ISP Router Interface Wizard Line'

    name = fields.Char(string='Name')
    mac_address = fields.Char(string='MAC Address')
    type = fields.Char(string='Type')
    running = fields.Boolean(string='Running')
    disabled = fields.Boolean(string='Disabled')
    comment = fields.Char(string='Comment')
    wizard_id = fields.Many2one('isp.netdev.interface.wizard')

class IspRouterRouteWizard(models.Model):
    _name = 'isp.netdev.route.wizard'
    _description = 'ISP Router Route Wizard'

    line_ids = fields.One2many('isp.netdev.route.wizard.line', 'wizard_id', string='Routes')
    router_id = fields.Many2one('isp.netdev')

class IspRouterRouteWizardLine(models.Model):
    _name = 'isp.netdev.route.wizard.line'
    _description = 'ISP Router Route Wizard Line'

    dst_address = fields.Char(string='Destination')
    gateway = fields.Char(string='Gateway')
    distance = fields.Integer(string='Distance')
    active = fields.Boolean(string='Active')
    static = fields.Boolean(string='Static')
    comment = fields.Char(string='Comment')
    wizard_id = fields.Many2one('isp.netdev.route.wizard')


class IspRouterPppActiveWizard(models.Model):
    _name = 'isp.netdev.ppp.active.wizard'
    _description = 'ISP Router PPP Active Wizard'

    name = fields.Char(string='Name')
    router_id = fields.Many2one('isp.netdev', string='Router', required=True)
    line_ids = fields.One2many('isp.netdev.ppp.active.wizard.line', 'wizard_id', string='Active Connections')

    #line_ids = fields.One2many('isp.netdev.ppp.active.wizard.line', 'wizard_id', string='Active Connections')
    #router_id = fields.Many2one('isp.netdev')
    ppp_speed_chart = fields.Text(string="PPP Speed Chart", readonly=True)

    @api.model
    def get_speed_data(self, wizard_id):
        # This is a placeholder for the actual data fetching logic.
        # You should replace this with your logic to get the speed data.
        import random
        return [random.randint(1, 100)]

    def action_get_active_connections(self):
        # ... (existing code)
        pass

class IspRouterPppActiveLine(models.TransientModel):
    _name = 'isp.netdev.ppp.active.line'
    ppp_speed_chart = fields.Text(string="PPP Speed Chart", readonly=True)

    def get_speed_data(self):
        # This is a placeholder. In a real implementation, you would fetch data from the router.
        # For now, we'll just return some random data.
        import random
        upload = [(i, random.randint(100, 500)) for i in range(20)]
        download = [(i, random.randint(500, 1500)) for i in range(20)]
        return {'upload': upload, 'download': download}

class IspRouterPppActiveWizardLine(models.Model):
    _name = 'isp.netdev.ppp.active.wizard.line'
    _description = 'ISP Router PPP Active Connections Wizard Line'

    name = fields.Char(string='Name')
    service = fields.Char(string='Service')
    caller_id = fields.Char(string='Caller ID')
    address = fields.Char(string='IP Address')
    uptime = fields.Char(string='Uptime')
    wizard_id = fields.Many2one('isp.netdev.ppp.active.wizard')
    ppp_speed_chart = fields.Text(string="PPP Speed Chart", readonly=True)

    def action_open_speed_chart(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'name': 'PPP Active Connection Speed',
        }

    @api.model
    def get_interface_speed(self, line_id):
        print(f"get_interface_speed called for line_id: {line_id}")
        line = self.browse(line_id)
        print(("linemmm", line))
        if not line:
            print("Line not found")
            return {'upload': 0, 'download': 0}

        router = line.wizard_id.router_id
        print(f"Router: {line} {router}")

        api = router._get_api_connection()
        if not api:
            print("Failed to get API connection")
            return {'upload': 0, 'download': 0}
        
        try:
            # The PPP username (e.g., '4064')
            ppp_user_name = line.name
            
            # Construct the dynamic interface name based on the pattern provided by the user
            interface_name_to_find = f"<pppoe-{ppp_user_name}>"
            
            print(f"Constructed interface name to monitor: {interface_name_to_find}")

            interface_path = api.path('/interface')

            # Now, monitor traffic using the constructed interface name
            traffic_generator = interface_path('monitor-traffic', interface=interface_name_to_find, once=True)
            
            traffic = next(traffic_generator, None)

            print(f"Traffic result for '{interface_name_to_find}': {traffic}")

            if traffic:
                tx_speed = traffic.get('tx-bits-per-second', 0)
                rx_speed = traffic.get('rx-bits-per-second', 0)
                print(f"Speeds: upload={tx_speed}, download={rx_speed}")
                return {'upload': tx_speed, 'download': rx_speed}
            else:
                print(f"monitor-traffic returned no data for interface '{interface_name_to_find}'.")
                return {'upload': 0, 'download': 0}

        except Exception as e:
            # The most likely error here is TrapError if the interface name is still not found.
            print(f"An exception occurred in get_interface_speed: {e}")
            import traceback
            traceback.print_exc()
            return {'upload': 0, 'download': 0}
        finally:
            if api:
                api.close()
                print("API connection closed.")
        
        return {'upload': 0, 'download': 0}

class IspRouterFirewallWizard(models.Model):
    _name = 'isp.netdev.firewall.wizard'
    _description = 'ISP Router Firewall Rules Wizard'

    line_ids = fields.One2many('isp.netdev.firewall.wizard.line', 'wizard_id', string='Firewall Rules')
    router_id = fields.Many2one('isp.netdev')

class IspRouterFirewallWizardLine(models.Model):
    _name = 'isp.netdev.firewall.wizard.line'
    _description = 'ISP Router Firewall Rules Wizard Line'

    chain = fields.Char(string='Chain')
    action = fields.Char(string='Action')
    src_address = fields.Char(string='Src. Address')
    dst_address = fields.Char(string='Dst. Address')
    protocol = fields.Char(string='Protocol')
    comment = fields.Char(string='Comment')
    disabled = fields.Boolean(string='Disabled')
    wizard_id = fields.Many2one('isp.netdev.firewall.wizard')

class IspRouterQueueWizard(models.Model):
    _name = 'isp.netdev.queue.wizard'
    _description = 'ISP Router Queues Wizard'

    line_ids = fields.One2many('isp.netdev.queue.wizard.line', 'wizard_id', string='Queues')
    router_id = fields.Many2one('isp.netdev')

class IspRouterQueueWizardLine(models.Model):
    _name = 'isp.netdev.queue.wizard.line'
    _description = 'ISP Router Queues Wizard Line'

    name = fields.Char(string='Name')
    target = fields.Char(string='Target')
    max_limit = fields.Char(string='Max Limit')
    burst_limit = fields.Char(string='Burst Limit')
    disabled = fields.Boolean(string='Disabled')
    comment = fields.Char(string='Comment')
    wizard_id = fields.Many2one('isp.netdev.queue.wizard')