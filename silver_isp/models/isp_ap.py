from odoo import models, fields

class IspAp(models.Model):
    _name = 'isp.ap'
    _description = 'Punto de acceso inalámbrico'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _inherits = {'isp.asset': 'asset_id'}

    asset_id = fields.Many2one('isp.asset', required=True, ondelete="cascade")


    hostname_ap = fields.Char(string='Hostname')
    software_version = fields.Char(string='Version Software')
    node_ids = fields.Many2many('isp.node', string='Nodos', readonly=True)

    description_brand = fields.Text(string='Descripcion', related='brand_id.description')
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

    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='ap',
        store=True,
        readonly=False
    )

    state = fields.Selection([('down', 'Down'), ('active', 'Active')], string='Estado', default='down')

    def action_connect_ap(self):
        self.ensure_one()
        # Simulate connection test
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection Test',
                'message': 'Connection to AP was successful!',
                'type': 'success',
            }
        }
