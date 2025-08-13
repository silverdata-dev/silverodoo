from odoo import models, fields

class IspBox(models.Model):
    _name = 'isp.box'
    _description = 'Caja de Conexion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'isp.asset': 'asset_id',
                 'isp.netdev':'netdev_id'}

    asset_id = fields.Many2one('isp.asset', required=True, ondelete="cascade")
    netdev_id = fields.Many2one('isp.netdev', required=True, ondelete="cascade")

    port_splitter_secondary = fields.Integer(string='Puerto Splitter Secundario')
    splitter_id = fields.Many2one('isp.splitter', string='Spliter Secundario')
    node_id = fields.Many2one('isp.node', string='Nodo', readonly=True)
    capacity_nap = fields.Selection([], string='Total NAP')
    capacity_usage_nap = fields.Integer(string='Usada NAP', readonly=True)


    s_vlan = fields.Integer(string='s-vlan')
    c_vlan = fields.Integer(string='c-vlan')


    is_line_nap = fields.Boolean(string='Gestion Vlan NAP', readonly=True)


    pri_onu_standar = fields.Char(string='PRI ONU Standar:')
    pri_onu_bridge = fields.Char(string='PRI ONU Bridge:')
    onu_ids_isp = fields.One2many('isp.onu.line', 'box_id', string='One serie')

    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='cto',
        store=True,
        readonly=False
    )