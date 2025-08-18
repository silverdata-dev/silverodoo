from odoo import models, fields, api

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
    contract_count = fields.Integer(string="Contratos", compute='_compute_contract_count')



    @api.model
    def create(self, vals):
        if vals.get('splitter_id'):
            splitter = self.env['isp.splitter'].browse(vals['splitter_id'])
            if splitter.exists():
                box_count = self.search_count([('splitter_id', '=', splitter.id)])
                vals['name'] = f"{splitter.name}/BOX{box_count + 1}"
        return super(IspBox, self).create(vals)

    def write(self, vals):
        if 'splitter_id' in vals:
            new_splitter = self.env['isp.splitter'].browse(vals['splitter_id'])
            if new_splitter.exists():
                for record in self:
                    box_count = self.search_count([('splitter_id', '=', new_splitter.id)])
                    record.name = f"{new_splitter.name}/BOX{box_count + 1}"
        return super(IspBox, self).write(vals)

    def _compute_contract_count(self):
        for record in self:
            # Assuming 'isp.contract' has a 'box_id' field.
            record.contract_count = self.env['isp.contract'].search_count([('box_id', '=', record.id)])

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': 'Contratos',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.contract',
            'view_mode': 'tree,form',
            'domain': [('box_id', '=', self.id)],
            'context': {'default_box_id': self.id},
            'target': 'current',
        }