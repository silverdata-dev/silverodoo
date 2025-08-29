from odoo import models, fields, api

class IspAp(models.Model):
    _name = 'isp.ap'
    _description = 'Punto de acceso inalámbrico'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _inherits = {'isp.asset': 'asset_id',
                 'isp.netdev':'netdev_id'}

    asset_id = fields.Many2one('isp.asset', required=True, ondelete="cascade")
    netdev_id = fields.Many2one('isp.netdev', required=True, ondelete="cascade")


    

    hostname_ap = fields.Char(string='Hostname')
    node_ids = fields.Many2many('isp.node', string='Nodos', readonly=False)

    description_brand = fields.Text(string='Descripcion', related='brand_id.description')



    capacity_usage_ap = fields.Integer(string='Usada AP', readonly=False)
    contract_count = fields.Integer(string="Contratos", compute='_compute_contract_count')
    core_id = fields.Many2one('isp.core', 'Equipo Core')
    is_mgn_mac_onu = fields.Boolean(string='Gestion MAC ONU')
    device_pool_ip_ids = fields.One2many('device.pool.ip', 'ap_id', string='Device Pool Ip')

    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='ap',
        store=True,
        readonly=False
    )

    netdev_type = fields.Selection(
        related='netdev_id.netdev_type',
        default='ap',
        store=True,
        readonly=False
    )

    state = fields.Selection([('down', 'Down'), ('active', 'Active')], string='Estado', default='down')


    @api.model
    def create(self, vals):
        print(("createee", vals))
        if vals.get('core_id'):
            core = self.env['isp.core'].browse(vals['core_id'])
            print(("createee0", core, core.name, core.asset_id, core.asset_id.name))
            if core.exists() and core.name:

                vals['parent_id'] = core.asset_id.id

                vals['name'] = f"{core.name}/{vals.get('hostname_ap', '')}"
                print(("createe2e", vals))
        print(("createee3", vals))
        return super(IspAp, self).create(vals)


    def write(self, vals):
        print(("apwrite", vals))

        for i, record in enumerate(self):
            if vals.get('core_id'):
                core = self.env['isp.core'].browse(vals['core_id'])
            else:
                core = record.core_id

            if core.exists() and core.name:
                hostname = vals.get('hostname_ap', record.hostname_ap)
                record.asset_id.name = f"{core.name}/{hostname}"
                record.parent_id = core.asset_id.id
                print(("cocrewr2", hostname))

            # If node_id is set to False, the name is not changed.
        return super(IspAp, self).write(vals)


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

    def _compute_contract_count(self):
        for record in self:
            # Assuming 'isp.contract' has a 'ap_id' field.
            record.contract_count = self.env['isp.contract'].search_count([('ap_id', '=', record.id)])

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': 'Contratos',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.contract',
            'view_mode': 'tree,form',
            'domain': [('ap_id', '=', self.id)],
            'context': {'default_ap_id': self.id},
            'target': 'current',
        }
