from odoo import models, fields

class IspAp(models.Model):
    _name = 'isp.ap'
    _description = 'Punto de acceso inalámbrico'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='AP')
    hostname_ap = fields.Char(string='Hostname')
    software_version = fields.Char(string='Version Software')
    node_ids = fields.Many2many('isp.node', string='Nodos', readonly=True)
    brand_ap_id = fields.Many2one('product.brand', string='Marca')
    model_ap = fields.Char(string='Modelo')
    description_brand = fields.Text(string='Descripcion', related='brand_ap_id.description')
    ip_ap = fields.Char(string='IP de Conexion')
    port_ap = fields.Char(string='Puerto de Conexion')
    user_ap = fields.Char(string='Usuario')
    password_ap = fields.Char(string='Password')
    type_access_net = fields.Selection([], string='Tipo Acceso', required=True)
    dhcp_custom_server = fields.Char(string='DHCP Leases')
    interface = fields.Char(string='Interface')
    is_dhcp_static = fields.Boolean(string='Habilitar Dhcp Static')
    capacity_usage_ap = fields.Integer(string='Usada AP', readonly=True)
    is_mgn_mac_onu = fields.Boolean(string='Gestion MAC ONU')
    device_pool_ip_ids = fields.One2many('device.pool.ip', 'ap_id', string='Device Pool Ip')
    country_id = fields.Many2one('res.country', string='Pais')
    state_id = fields.Many2one('res.country.state', string='Provincia')
    zip = fields.Char(string='Cod.Postal')
    street = fields.Char(string='Direccion')
    street2 = fields.Char(string='-')
    ap_latitude = fields.Float(string='Latitude', digits=(16, 7))
    ap_longitude = fields.Float(string='Longitude', digits=(16, 7))
    date_localization = fields.Date(string='Actualizado el:')
    state = fields.Selection([('down', 'Down'), ('active', 'Active')], string='Estado', default='down')

    def action_connect_ap(self):
        pass
