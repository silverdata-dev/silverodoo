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



    node_id = fields.Many2one('silver.node', string='Nodo')
    core_id = fields.Many2one('silver.core', 'Equipo Core')
    hostname_ap = fields.Char(string='Hostname')
    node_ids = fields.Many2many('silver.node', string='Nodos', readonly=False)

    #description_brand = fields.Text(string='Descripcion', related='brand_id.description')



    capacity_usage_ap = fields.Integer(string='Usada AP', readonly=False)


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




    def generar(self):
        for record in self:
            record.netdev_id.generar()



    @api.onchange('node_id')
    def _onchange_node_id(self):
        # Primero, verifica si hay un nodo principal anterior para eliminarlo

        previous_nodes_ids = self._origin.node_ids.ids
        print(("previus", previous_nodes_ids))

        # Si había un nodo principal anterior, lo removemos de la lista
        if self._origin.node_id:
            # Creamos un conjunto para una eliminación más eficiente
            nodes_set = set(previous_nodes_ids)
            nodes_set.discard(self._origin.node_id.id)
            current_nodes_ids = list(nodes_set)
        else:
            current_nodes_ids = previous_nodes_ids

        # Ahora, agregamos el ID del nuevo nodo principal si existe
        if self.node_id:
            if self.node_id.id not in current_nodes_ids:
                current_nodes_ids.append(self.node_id.id)

        # Asignar la lista final de IDs al campo many2many usando el comando (6,0,...)
        self.node_ids = [(6, 0, current_nodes_ids)]

    def button_test_connection(self):
        si = False
        for core in self:
            if core.netdev_id:
                try:
                    is_successful = core.netdev_id.button_test_connection()
                    if is_successful:
                        core.state = 'active'
                        si = True
                    else:
                        core.state = 'down'
                except Exception:
                    core.state = 'down'
            else:
                core.state = 'down'

        if si:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Test'),
                    'message': _('Connection to Core was successful!'),
                    'type': 'success',
                    'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                }
            }
        # If the connection fails, we still reload to show the 'down' state.
        return {'type': 'ir.actions.client', 'tag': 'reload'}
