from odoo import models, fields, api

class SilverAp(models.Model):
    _name = 'silver.ap'
    #_table = 'isp_ap'
    _description = 'Punto de acceso inalámbrico'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    _inherits = {'silver.asset': 'asset_id',
                 'silver.netdev':'netdev_id'}

    asset_id = fields.Many2one('silver.asset', required=True, ondelete="cascade")
    netdev_id = fields.Many2one('silver.netdev', required=True, ondelete="cascade")


    

    hostname_ap = fields.Char(string='Hostname')
    node_ids = fields.Many2many('silver.node', string='Nodos', readonly=False)

    #description_brand = fields.Text(string='Descripcion', related='brand_id.description')



    capacity_usage_ap = fields.Integer(string='Usada AP', readonly=False)

    core_id = fields.Many2one('silver.core', 'Equipo Core')
    is_mgn_mac_onu = fields.Boolean(string='Gestion MAC ONU')
    device_pool_ip_ids = fields.One2many('silver.device.pool.ip', 'ap_id', string='Device Pool Ip')

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
            core = self.env['silver.core'].browse(vals['core_id'])
            print(("createee0", core, core.name, core.asset_id, core.asset_id.name))
            if core.exists() and core.name:

                vals['parent_id'] = core.asset_id.id

                vals['name'] = f"{core.name}/{vals.get('hostname_ap', '')}"
                print(("createe2e", vals))
        print(("createee3", vals))
        return super(SilverAp, self).create(vals)


    def write(self, vals):
        print(("apwrite", vals))

        for record in self:
            if vals.get('core_id'):
                core = self.env['silver.core'].browse(vals['core_id'])
            else:
                core = record.core_id

            if core.exists() and core.name and 'parent_id' not in vals:
                hostname = vals.get('hostname_ap', record.hostname_ap)
                record.asset_id.name = f"{core.name}/{hostname}"
                record.parent_id = core.asset_id.id
                print(("cocrewr2", hostname))

            # If node_id is set to False, the name is not changed.
        return super(SilverAp, self).write(vals)


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


    def generar(self):
        for record in self:
            record.netdev_id.generar()
