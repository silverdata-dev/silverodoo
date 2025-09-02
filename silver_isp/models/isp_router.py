# -*- coding: utf-8 -*-

from odoo import models, fields, api
import librouteros

class IspRouter(models.Model):
    _name = 'isp.netdev'
    _description = 'ISP Router'

    name = fields.Char(string='Router Name', required=True)
    hostname = fields.Char(string='Hostname/IP', required=True)
    username = fields.Char(string='Username', required=True)
    password = fields.Char(string='Password', password=True, required=True)
    api_port = fields.Integer(string='API Port', default=21000, required=True)
    
    is_active = fields.Boolean(string='Active', default=True)
    vendor = fields.Selection([
        ('mikrotik', 'MikroTik'),
        # Add other vendors here in the future
    ], string='Vendor', default='mikrotik', required=True)
    
    model = fields.Char(string='Model', readonly=True)
    firmware_version = fields.Char(string='Firmware Version', readonly=True)
    serial_number = fields.Char(string='Serial Number', readonly=True)
    
    state = fields.Selection([
        ('connected', 'Connected'),
        ('connecting', 'Connecting'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error')
    ], string='Status', default='disconnected', readonly=True)

    def _get_api_connection(self):
        self.ensure_one()
        try:
            self.write({'state': 'connecting'})
            print(("connect", {
                "host":self.hostname,
                "username":self.username,
                "password":self.password,
                "port":self.api_port
            }))
            api = librouteros.connect(
                host=self.hostname,
                username=self.username,
                password=self.password,
                port=self.api_port
            )
            self.write({'state': 'connected'})
            return api
        except (librouteros.exceptions.TrapError, ConnectionRefusedError) as e:
            print(("error", e))
            self.write({'state': 'error'})
            # Consider logging the error e
            return None

    def button_test_connection(self):
        for router in self:
            api = router._get_api_connection()
            if api:
                api.close()
                # Optionally, add a user notification for success
        return True

    def button_get_system_info(self):
        for router in self:
            api = router._get_api_connection()
            if api:
                try:
                    system_resource = tuple(api.path('/system/resource'))[0]
                    routerboard_info = tuple(api.path('/system/routerboard'))[0]

                    print(("system_resource", system_resource,"routerboard_info",routerboard_info ))
                    
                    router.write({
                        'model': routerboard_info.get('model'),
                        'firmware_version': system_resource.get('version'),
                        'serial_number': routerboard_info.get('serial-number'),
                    })
                finally:
                    api.close()
        return True

    def button_view_interfaces(self):
        self.ensure_one()
        api = self._get_api_connection()
        if not api:
            return

        try:
            interfaces = tuple(api.path('/interface'))
            wizard = self.env['isp.netdev.interface.wizard'].create({'router_id': self.id})
            for interface in interfaces:
                self.env['isp.netdev.interface.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'name': interface.get('name'),
                    'mac_address': interface.get('mac-address'),
                    'type': interface.get('type'),
                    'running': interface.get('running'),
                    'disabled': interface.get('disabled'),
                    'comment': interface.get('comment'),
                })
            
            return {
                'name': 'Router Interfaces',
                'type': 'ir.actions.act_window',
                'res_model': 'isp.netdev.interface.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        finally:
            api.close()

    def button_view_routes(self):
        self.ensure_one()
        api = self._get_api_connection()
        if not api:
            return

        try:
            routes = tuple(api.path('/ip/route'))
            wizard = self.env['isp.netdev.route.wizard'].create({'router_id': self.id})
            for route in routes:
                self.env['isp.netdev.route.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'dst_address': route.get('dst-address'),
                    'gateway': route.get('gateway'),
                    'distance': route.get('distance'),
                    'active': route.get('active'),
                    'static': route.get('static'),
                    'comment': route.get('comment'),
                })
            
            return {
                'name': 'Router Routes',
                'type': 'ir.actions.act_window',
                'res_model': 'isp.netdev.route.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        finally:
            api.close()

    def button_view_ppp_active(self):
        self.ensure_one()
        api = self._get_api_connection()
        if not api:
            return

        try:
            ppp_active = tuple(api.path('/ppp/active'))
            wizard = self.env['isp.netdev.ppp.active.wizard'].create({'router_id': self.id})
            for ppp in ppp_active:
                self.env['isp.netdev.ppp.active.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'name': ppp.get('name'),
                    'service': ppp.get('service'),
                    'caller_id': ppp.get('caller-id'),
                    'address': ppp.get('address'),
                    'uptime': ppp.get('uptime'),
                })
            
            return {
                'name': 'PPP Active Connections2',
                'type': 'ir.actions.act_window',
                'res_model': 'isp.netdev.ppp.active.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        finally:
            api.close()

    def button_view_firewall_rules(self):
        self.ensure_one()
        api = self._get_api_connection()
        if not api:
            return

        try:
            firewall_rules = tuple(api.path('/ip/firewall/filter'))
            wizard = self.env['isp.netdev.firewall.wizard'].create({'router_id': self.id})
            for rule in firewall_rules:
                self.env['isp.netdev.firewall.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'chain': rule.get('chain'),
                    'action': rule.get('action'),
                    'src_address': rule.get('src-address'),
                    'dst_address': rule.get('dst-address'),
                    'protocol': rule.get('protocol'),
                    'comment': rule.get('comment'),
                    'disabled': rule.get('disabled'),
                })
            
            return {
                'name': 'Firewall Rules',
                'type': 'ir.actions.act_window',
                'res_model': 'isp.netdev.firewall.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        finally:
            api.close()

    def button_view_queues(self):
        self.ensure_one()
        api = self._get_api_connection()
        if not api:
            return

        try:
            queues = tuple(api.path('/queue/simple'))
            wizard = self.env['isp.netdev.queue.wizard'].create({'router_id': self.id})
            for queue in queues:
                self.env['isp.netdev.queue.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'name': queue.get('name'),
                    'target': queue.get('target'),
                    'max_limit': queue.get('max-limit'),
                    'burst_limit': queue.get('burst-limit'),
                    'disabled': queue.get('disabled'),
                    'comment': queue.get('comment'),
                })
            
            return {
                'name': 'Queues',
                'type': 'ir.actions.act_window',
                'res_model': 'isp.netdev.queue.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        finally:
            api.close()
