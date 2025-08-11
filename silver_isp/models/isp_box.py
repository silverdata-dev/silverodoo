from odoo import models, fields

class IspBox(models.Model):
    _name = 'isp.box'
    _description = 'Caja de Conexion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'isp.asset': 'asset_id'}

    asset_id = fields.Many2one('isp.asset', required=True, ondelete="cascade")

    port_splitter_secondary = fields.Integer(string='Puerto Splitter Secundario')
    splitter_id = fields.Many2one('isp.splitter', string='Spliter Secundario')
    node_id = fields.Many2one('isp.node', string='Nodo', readonly=True)
    capacity_nap = fields.Selection([], string='Total NAP')
    capacity_usage_nap = fields.Integer(string='Usada NAP', readonly=True)
    country_id = fields.Many2one('res.country', string='Pais')
    state_id = fields.Many2one('res.country.state', string='Provincia')
    zip = fields.Char(string='Cod.Postal')
    street = fields.Char(string='Direccion')
    street2 = fields.Char(string='-')
    node_latitude = fields.Float(string='Customer Latitude', digits=(16, 7))
    node_longitude = fields.Float(string='Customer Longitude', digits=(16, 7))
    date_localization = fields.Date(string='Actualizado el:')
    s_vlan = fields.Integer(string='s-vlan')
    c_vlan = fields.Integer(string='c-vlan')
    type_access_net = fields.Selection([], string='Tipo')
    is_line_nap = fields.Boolean(string='Gestion Vlan NAP', readonly=True)
    dhcp_custom_server = fields.Char(string='DHCP Leases')
    dhcp_client = fields.Boolean(string='Profiles VSOL')
    pri_onu_standar = fields.Char(string='PRI ONU Standar:')
    pri_onu_bridge = fields.Char(string='PRI ONU Bridge:')
    onu_ids_isp = fields.One2many('isp.onu.line', 'box_id', string='One serie')
