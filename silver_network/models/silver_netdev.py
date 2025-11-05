from odoo import models, fields, api, _
from odoo.exceptions import UserError
import librouteros
from odoo.http import request
from ..models.olt_connection import OLTConnection

import logging

_logger = logging.getLogger(__name__)


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

class SilverNetdev(models.Model):
    _name = 'silver.netdev'
    #_table = 'isp_netdev'
    _description = 'ISP Network Device (Base Model)'

    #name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    netdev_type = fields.Selection([
        ('ap', 'AP'),
        ('core', 'Core'),
        ('nap', 'NAP'),
        ('olt', 'OLT'),
        ('port', 'Port'),
        ('radius', 'Radius'),
        ('other', 'Other')
    ], default='other')

    type_access_net = fields.Selection(
        [('inactive', 'Inactivo'), ('dhcp', 'DHCP Leases'), ('manual', 'IP Asignada manualmente'),
         ('system', 'IP Asiganada por el sistema')], default='inactive', string='Tipo Acceso', required=True)


    dhcp_custom_server = fields.Char(string='DHCP Leases')
    interface = fields.Char(string='Interface')
    is_dhcp_static = fields.Boolean(string='Habilitar Dhcp Static')
    dhcp_client = fields.Boolean(string='Profiles VSOL')


    ip_address_pool_ids = fields.One2many('silver.ip.address.pool', 'netdev_id', string='Direcciones IP')
    ip_address_ids = fields.One2many('silver.ip.address', 'netdev_id', string='Direcciones IP')



    ip = fields.Char(string='IP de Conexion')
    port = fields.Char(string='Puerto de Conexion')
    username = fields.Char(string='Usuario')
    password = fields.Char(string='Password')
    type_connection = fields.Selection([("ssh","SSH"), ("telnet", "Telnet")], string='Tipo de Conexión')
    port_telnet = fields.Char(string='Puerto telnet', default=23)
    port_ssh = fields.Char(string='Puerto ssh', default=22)

    #api_hostname = fields.Char(string='Hostname/IP', required=True)
    api_port = fields.Integer(string='API Port', default=21000, required=True)


    state = fields.Selection([('down', 'Down'), ('active', 'Active'), ('connected', 'Connected'),
        ('connecting', 'Connecting'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error')],

                             string='Estado', default='down')

    # Fields for Radius Client Configuration
    radius_client_ip = fields.Char(string='Radius Server IP')
    radius_client_secret = fields.Char(string='Radius Shared Secret')
    radius_client_services = fields.Many2many('silver.radius.service', string='Radius Services') # Assuming a model silver.radius.service exists or will be created

    #core_ids = fields.One2many('silver.core', 'netdev_id', string='Cores')
    #olt_ids = fields.One2many('silver.olt', 'netdev_id', string='OLTs')
    #olt_card_port_ids = fields.One2many('silver.olt.card.port', 'netdev_id', string='OLT Card Ports')
    #box_ids = fields.One2many('silver.box', 'netdev_id', string='Boxes')
    #ap_ids = fields.One2many('silver.ap', 'netdev_id', string='APs')
    #radius_ids = fields.One2many('silver.radius', 'netdev_id', string='Radius Servers')

    def generar(self):
        for ret in self.ip_address_pool_ids:
            ret.action_generate_ips()

    def _get_api_connection(self, username=None, password=None):
        self.ensure_one()
        p = self.port or self.api_port

        # Use provided credentials, fallback to self, then to session
        user_to_try = username or self.username or request.session.get('radius_user')
        pass_to_try = password or self.password or request.session.get('radius_password')

        if not user_to_try or not pass_to_try:
            #self.write({'state': 'error'})
            self.state = 'error'
            _logger.error("Connection attempt failed: No username or password provided.")
            return None

        try:
            self.state = 'connecting'
           # self.write({'state': 'connecting'})
            _logger.info(f"Attempting to connect to {self.ip}:{p} with user '{user_to_try}'")
            api = librouteros.connect(
                host=self.ip,
                username=user_to_try,
                password=pass_to_try,
                port=int(p),
                encoding='latin-1'
            )
            _logger.info(f"Successfully connected to {self.ip}")
            #self.write({'state': 'connected'})
            self.state = 'connected'
            return api
        except Exception as e:
            _logger.error(f"Failed to connect to {self.ip}:{p} with user '{user_to_try}'. Error: {e}")
            self.state = 'error'
            #self.write({'state': 'error'})
            return None

    def _get_olt_connection(self):
        self.ensure_one()
        return OLTConnection(
            host=self.ip,
            port=(self.port_ssh if self.type_connection=='ssh'  else self.port_telnet),
            username=self.username,
            password=self.password,
            connection_type=self.type_connection,
        )

    def get_real_model_name_by_id(self):
        print("get real")
        return self.model

    def button_add_update_radius_client(self):
        self.ensure_one()
        if not self.ip:  # or not self.radius_client_secret:
            raise UserError(("Radius Server IP and Shared Secret are required."))

        api = self._get_api_connection()
        if api:
            try:
                # Check if Radius client for this IP already exists
                r=api.path('/radius')
                print(("radius", r, dir(r), api.path('/radius')))
                existing_client = api.path('/radius').get(address=self.ip)
                #tuple(api.path('/system/resource'))[0]
                
                services_str = ",".join(self.radius_client_services.mapped('name')) if self.radius_client_services else ""

                if existing_client:
                    # Update existing client
                    api.path('/radius').set(
                        **{'.id': existing_client[0]['.id'],
                           'secret': self.radius_client_secret,
                           'service': services_str,
                           'authentication': 'yes',
                           'accounting': 'yes'}
                    )
                    message = "Radius client updated successfully!"
                else:
                    # Add new client
                    api.path('/radius').add(
                        address=self.ip,
                        secret=self.radius_client_secret,
                        service=services_str,
                        authentication='yes',
                        accounting='yes'
                    )
                    message = "Radius client added successfully!"
                
                self.write({'state': 'connected'})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': message,
                        'type': 'success',
                    }
                }
            except Exception as e:
                self.write({'state': 'error'})
                raise UserError(("Failed to configure Radius client: %s") % e)
            finally:
                api.close()
        else:
            raise UserError(_("Could not connect to the MikroTik router."))

    def button_remove_radius_client(self):
        self.ensure_one()
        if not self.radius_client_ip:
            raise UserError(_("Radius Server IP is required to remove the client."))

        api = self._get_api_connection()
        if api:
            try:
                existing_client = api.path('/radius').get(address=self.radius_client_ip)
                if existing_client:
                    api.path('/radius').remove(id=existing_client[0]['.id'])
                    message = "Radius client removed successfully!"
                else:
                    message = "Radius client not found for this IP."
                
                self.write({'state': 'connected'})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': message,
                        'type': 'success',
                    }
                }
            except Exception as e:
                self.write({'state': 'error'})
                raise UserError(_("Failed to remove Radius client: %s") % e)
            finally:
                api.close()
        else:
            raise UserError(_("Could not connect to the MikroTik router."))

    @api.model
    def button_test_connection(self):
        print("test")
        self.ensure_one()
        api = self._get_api_connection()
        if api:
            api.close()
            return True
        return False

    def button_get_system_info(self):
        self.ensure_one()
        api = self._get_api_connection()
        if not api:
            raise UserError(_("Could not connect to the device."))

        info_str = ""
        try:
            # Get System Resource
            resource = tuple(api.path('/system/resource'))
            if resource:
                info_str += "--- System Resources ---\n"
                for key, value in resource[0].items():
                    info_str += f"{key.replace('-', ' ').title()}: {value}\n"
                info_str += "\n"

            # Get System Health
            health = tuple(api.path('/system/health'))
            if health:
                info_str += "--- System Health ---\n"
                for key, value in health[0].items():
                    info_str += f"{key.replace('-', ' ').title()}: {value}\n"
                info_str += "\n"

            # Get RouterBoard Info
            routerboard = tuple(api.path('/system/routerboard'))
            if routerboard:
                info_str += "--- RouterBoard ---\n"
                for key, value in routerboard[0].items():
                    info_str += f"{key.replace('-', ' ').title()}: {value}\n"

            wizard = self.env['silver.netdev.system.info.wizard'].create({
                'info': info_str,
                'netdev_id': self.id
            })

            return {
                'name': 'System Information',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.system.info.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }

        except Exception as e:
            raise UserError(_("Failed to fetch system info: %s") % e)
        finally:
            api.close()

    def button_view_interfaces(self):
        self.ensure_one()
        api = self._get_api_connection()
        if not api:
            return

        try:
            wizard = self.env['silver.netdev.interface.wizard'].create({
                'netdev_id': self.id
            })

            # Helper function to create records to avoid repetition
            def create_lines(model_name, data, mapping, traffic_map):
                model = self.env[model_name]
                for item in data:
                    vals = {'wizard_id': wizard.id}
                    for odoo_field, mikrotik_field in mapping.items():
                        vals[odoo_field] = item.get(mikrotik_field)
                    
                    # Add traffic data by looking up the interface name
                    name = item.get('name')
                    if name in traffic_map:
                        traffic = traffic_map[name]
                        vals['rx_speed'] = _format_speed(traffic.get('rx-bits-per-second', 0))
                        vals['tx_speed'] = _format_speed(traffic.get('tx-bits-per-second', 0))
                    
                    model.create(vals)

            # 1. General Interfaces (Main Tab)
            interfaces = tuple(api.path('/interface'))
            interface_names = [iface.get('name') for iface in interfaces]
            
            # MikroTik's monitor-traffic has a limit on the number of interfaces.
            # We process them in chunks to avoid the error.
            traffic_map = {}
            chunk_size = 90  # A safe limit below 100
            for i in range(0, len(interface_names), chunk_size):
                chunk = interface_names[i:i + chunk_size]
                traffic_chunk_data = api.path('/interface')('monitor-traffic', interface=",".join(chunk), once='')
                for item in traffic_chunk_data:
                    traffic_map[item['name']] = item

            for interface in interfaces:
                name = interface.get('name')
                traffic = traffic_map.get(name, {})
                self.env['silver.netdev.interface.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'name': name,
                    'mac_address': interface.get('mac-address'),
                    'type': interface.get('type'),
                    'running': interface.get('running'),
                    'disabled': interface.get('disabled'),
                    'comment': interface.get('comment'),
                    'rx_speed': _format_speed(traffic.get('rx-bits-per-second', 0)),
                    'tx_speed': _format_speed(traffic.get('tx-bits-per-second', 0)),
                })

            # 2. Ethernet
            ethernet_data = tuple(api.path('/interface/ethernet'))
            create_lines('silver.netdev.interface.ethernet.line', ethernet_data, {
                'name': 'name', 'mac_address': 'mac-address', 'mtu': 'mtu', 
                'l2mtu': 'l2mtu', 'arp': 'arp', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 3. EoIP Tunnels
            eoip_data = tuple(api.path('/interface/eoip'))
            create_lines('silver.netdev.interface.eoip.line', eoip_data, {
                'name': 'name', 'remote_address': 'remote-address', 'tunnel_id': 'tunnel-id',
                'mac_address': 'mac-address', 'mtu': 'mtu', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 4. GRE Tunnels
            gre_data = tuple(api.path('/interface/gre'))
            create_lines('silver.netdev.interface.gre.line', gre_data, {
                'name': 'name', 'remote_address': 'remote-address', 'local_address': 'local-address',
                'mtu': 'mtu', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 5. VLANs
            vlan_data = tuple(api.path('/interface/vlan'))
            create_lines('silver.netdev.interface.vlan.line', vlan_data, {
                'name': 'name', 'vlan_id': 'vlan-id', 'interface': 'interface',
                'mtu': 'mtu', 'arp': 'arp', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 6. VRRP
            vrrp_data = tuple(api.path('/interface/vrrp'))
            create_lines('silver.netdev.interface.vrrp.line', vrrp_data, {
                'name': 'name', 'interface': 'interface', 'vrid': 'vrid', 'priority': 'priority',
                'interval': 'interval', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 7. Bonding
            bonding_data = tuple(api.path('/interface/bonding'))
            create_lines('silver.netdev.interface.bonding.line', bonding_data, {
                'name': 'name', 'slaves': 'slaves', 'mode': 'mode', 
                'link_monitoring': 'link-monitoring', 'mtu': 'mtu', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 8. LTE
            lte_data = tuple(api.path('/interface/lte'))
            create_lines('silver.netdev.interface.lte.line', lte_data, {
                'name': 'name', 'mac_address': 'mac-address', 'mtu': 'mtu',
                'imei': 'imei', 'pin': 'pin-status', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            return {
                'name': 'Router Interfaces',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.interface.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('silver_network.view_silver_router_interface_wizard_form').id,
                'res_id': wizard.id,
                'target': 'new',
                'context': {
                    'default_netdev_id': self.id,
                }
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
            wizard = self.env['silver.netdev.route.wizard'].create({'router_id': self.id})
            for route in routes:
                self.env['silver.netdev.route.wizard.line'].create({
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
                'res_model': 'silver.netdev.route.wizard',
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
            wizard = self.env['silver.netdev.ppp.active.wizard'].create({'router_id': self.id})
            for ppp in ppp_active:
                self.env['silver.netdev.ppp.active.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'name': ppp.get('name'),
                    'service': ppp.get('service'),
                    'caller_id': ppp.get('caller-id'),
                    'address': ppp.get('address'),
                    'uptime': ppp.get('uptime'),
                })

            return {
                'name': 'PPP Active Connections1',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.ppp.active.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
                'context': {
                    'default_netdev_id': self.id,
                }
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
            wizard = self.env['silver.netdev.firewall.wizard'].create({'router_id': self.id})
            for rule in firewall_rules:
                self.env['silver.netdev.firewall.wizard.line'].create({
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
                'res_model': 'silver.netdev.firewall.wizard',
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
            wizard = self.env['silver.netdev.queue.wizard'].create({'router_id': self.id})
            for queue in queues:
                self.env['silver.netdev.queue.wizard.line'].create({
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
                'res_model': 'silver.netdev.queue.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
                'context': {
                    'default_netdev_id': self.id,
                }
            }
        finally:
            api.close()

    def get_formview_id(self, access_uid=None):
        self.ensure_one()
        if self.env['silver.core'].search([('netdev_id', '=', self.id)], limit=1):
            return self.env.ref('view_silver_core_form').id
        if self.env['silver.ap'].search([('netdev_id', '=', self.id)], limit=1):
            return self.env.ref('view_silver_ap_form').id
        return super().get_formview_id(access_uid=access_uid)

    def button_view_active_users(self):
        self.ensure_one()
        api = self._get_api_connection()
        if not api:
            return

        try:
            active_users = tuple(api.path('/user/active'))
            wizard = self.env['silver.netdev.active.users.wizard'].create({})
            
            for user in active_users:
                self.env['silver.netdev.active.users.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'name': user.get('name'),
                    'address': user.get('address'),
                    'via': user.get('via'),
                    'uptime': user.get('uptime'),
                })

            return {
                'name': 'Active Users',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.active.users.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        finally:
            if api:
                api.close()