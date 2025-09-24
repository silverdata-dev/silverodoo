from odoo import models, fields, api

class SilverBox(models.Model):
    _name = 'silver.box'
    _description = 'Caja de Conexion'
    #_table = 'isp_box'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'silver.asset': 'asset_id',
                 'silver.netdev':'netdev_id'}

    asset_id = fields.Many2one('silver.asset', required=True, ondelete="cascade")
    netdev_id = fields.Many2one('silver.netdev', required=True, ondelete="cascade")

    name = fields.Char(string="Nombre", related="asset_id.name", readonly=False)


    port_splitter_secondary = fields.Integer(string='Puerto Splitter Secundario')
    splitter_id = fields.Many2one('silver.splitter', string='Spliter Secundario')
    node_id = fields.Many2one('silver.node', string='Nodo')
    capacity_nap = fields.Selection([("8","8"), ("16", "16"), ("24", "24"), ("32", "32")], string='Total NAP')
    capacity_usage_nap = fields.Integer(string='Usada NAP')


    s_vlan = fields.Integer(string='s-vlan')
    c_vlan = fields.Integer(string='c-vlan')


    is_line_nap = fields.Boolean(string='Gestion Vlan NAP')


    ntrunk = fields.Integer(string='N de trunk')
    cabletype = fields.Selection([("adss", "Adss"), ("0","0"),("na","N/A")], string='Tipo de cable')
    cnstrands = fields.Selection([("0", "0"), ("12","12"), ("24","24"), ("96","96"), ("na","N/A")], "Cantidad de hilos")
    cnbuffer = fields.Selection([("0","0"), ("1","1"), ("4", "4"), ("8","8"),("na","N/A")], "Cantidad buffer")
    nbuffer = fields.Selection([("0","0"), ("1","1"), ("2","2"), ("3","3"),("4", "4"), ("T","T"),("na","N/A")], "N buffer")
    ndistro = fields.Char(string='N de distibución')
    nspliceclosure = fields.Char(string='N de manga')
    olt = fields.Char(string="OLT")
    pon = fields.Char(string='Pon')
    odf = fields.Char(string='Odf')
    note = fields.Char(string='Notas')



    pri_onu_standar = fields.Char(string='PRI ONU Standar:')
    pri_onu_bridge = fields.Char(string='PRI ONU Bridge:')
    onu_ids_silver = fields.One2many('silver.onu.line', 'box_id', string='One serie')

    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='cto',
        store=True,
        readonly=False
    )
    netdev_type = fields.Selection(
        related='netdev_id.netdev_type',
        default='cto',
        store=True,
        readonly=False
    )

    #contract_count = fields.Integer(string="Contratos", compute='_compute_contract_count')
 


    @api.model
    def create(self, vals):
        if vals.get('splitter_id'):
            splitter = self.env['silver.splitter'].browse(vals['splitter_id'])
            if splitter.exists():
                box_count = self.search_count([('splitter_id', '=', splitter.id)])
                vals['name'] = f"{splitter.name}/BOX{box_count + 1}"
        return super(SilverBox, self).create(vals)

    def write(self, vals):
        if 'splitter_id' in vals:
            new_splitter = self.env['silver.splitter'].browse(vals['splitter_id'])
            if new_splitter.exists():
                for record in self:
                    box_count = self.search_count([('splitter_id', '=', new_splitter.id)])
                    record.name = f"{new_splitter.name}/BOX{box_count + 1}"
        return super(SilverBox, self).write(vals)
