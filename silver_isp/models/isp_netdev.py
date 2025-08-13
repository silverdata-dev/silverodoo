from odoo import models, fields


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
    user = fields.Char(string='Usuario')
    password = fields.Char(string='Password')
    type_connection = fields.Selection([("ssh","SSH"), ("telnet", "Telnet")], string='Tipo de Conexión')


    state = fields.Selection([('down', 'Down'), ('active', 'Active')], string='Estado', default='down')
