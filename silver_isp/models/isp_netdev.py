from odoo import models, fields, api
import librouteros

class IspNetdev(models.Model):
    _name = 'isp.netdev'
    _description = 'ISP Network Device (Base Model)'



    type_access_net = fields.Selection(
        [('inactive', 'Inactivo'), ('dhcp', 'DHCP Leases'), ('manual', 'IP Asignada manualmente'),
         ('system', 'IP Asignada por el sistema')], default='inactive', string='Tipo Acceso', required=True)


    dhcp_custom_server = fields.Char(string='DHCP Leases')
    interface = fields.Char(string='Interface')
    is_dhcp_static = fields.Boolean(string='Habilitar Dhcp Static')
    dhcp_client = fields.Boolean(string='Profiles VSOL')
    software_version = fields.Char(string='Version Software')

    ip_address_line_ids = fields.One2many('isp.ip.address.line', 'core_id', string='Direcciones IP')
    ip_address_ids = fields.One2many('isp.ip.address', 'core_id', string='Direcciones IP')


    
    ip = fields.Char(string='IP de Conexion')
    port = fields.Char(string='Puerto de Conexion')
    username = fields.Char(string='Usuario')
    password = fields.Char(string='Password')
    type_connection = fields.Selection([("ssh","SSH"), ("telnet", "Telnet")], string='Tipo de Conexión')

    #api_hostname = fields.Char(string='Hostname/IP', required=True)
    api_port = fields.Integer(string='API Port', default=21000, required=True)
    vendor = fields.Selection([
        ('mikrotik', 'MikroTik'),
        # Add other vendors here in the future
    ], string='Vendor', default='mikrotik', required=True)
    firmware_version = fields.Char(string='Firmware Version', readonly=False)
    serial_number = fields.Char(string='Serial Number', readonly=False)

    state = fields.Selection([('down', 'Down'), ('active', 'Active'), ('connected', 'Connected'),
        ('connecting', 'Connecting'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error')], string='Estado', default='down')


    @api.model
    def _get_api_connection(self):
        self.ensure_one()
        try:
            self.write({'state': 'connecting'})
            print(("connect", {
                "host":self.ip,
                "username":self.username,
                "password":self.password,
                "port":self.api_port
            }))
            api = librouteros.connect(
                host=self.ip,
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

    @api.model
    def button_test_connection(self):
        for router in self:
            api = router._get_api_connection()
            if api:
                api.close()
                # Optionally, add a user notification for success
        return True

    @api.model
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

    @api.model

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

    @api.model
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

    @api.model
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
                'name': 'PPP Active Connections',
                'type': 'ir.actions.act_window',
                'res_model': 'isp.netdev.ppp.active.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        finally:
            api.close()

    @api.model
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

    @api.model
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
