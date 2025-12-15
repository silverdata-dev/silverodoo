from odoo import models, fields, api

class SilverBox(models.Model):
    _name = 'silver.box'
    _description = 'Caja de Conexion'
    #_table = 'isp_box'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char(string="Nombre")


    port_splitter_secondary = fields.Integer(string='Puerto Splitter Secundario')
    splitter_id = fields.Many2one('silver.splitter', string='Spliter Secundario')
    node_id = fields.Many2one('silver.node', string='Nodo')
    core_id = fields.Many2one( 'silver.core', string="Equipo Core", domain="[('node_id', '=', node_id)]")
    olt_id = fields.Many2one( 'silver.olt', string= 'OLT', domain= "[('core_id', '=', core_id)]")
    olt_port_id = fields.Many2one( 'silver.olt.card.port', string= 'PON', domain= "[('olt_id', '=', olt_id)]")

    capacity_nap = fields.Selection([("8","8"), ("16", "16"), ("24", "24"), ("32", "32")], string='Total NAP')
    capacity_usage_nap = fields.Integer(string='Usada NAP')


    s_vlan = fields.Integer(string='s-vlan')
    c_vlan = fields.Integer(string='c-vlan')


    is_line_nap = fields.Boolean(string='Gestion Vlan NAP')


    silver_address_id = fields.Many2one('silver.address', string='Dirección')


    ntrunk = fields.Integer(string='N de trunk')
    cabletype = fields.Selection([("adss", "Adss"), ("0","0"),("na","N/A")], string='Tipo de cable')
    cnstrands = fields.Selection([("0", "0"), ("12","12"), ("24","24"), ("96","96"), ("na","N/A")], "Cantidad de hilos")
    cnbuffer = fields.Selection([("0","0"), ("1","1"), ("4", "4"), ("8","8"),("na","N/A")], "Cantidad buffer")
    nbuffer = fields.Selection([("0","0"), ("1","1"), ("2","2"), ("3","3"),("4", "4"), ("T","T"),("na","N/A")], "N buffer")
    ndistro = fields.Char(string='N de distibución')
    nspliceclosure = fields.Char(string='N de manga')
 #   olt = fields.Char(string="OLT")
 #   pon = fields.Char(string='Pon')
#    odf = fields.Char(string='Odf')
    note = fields.Char(string='Notas')

    latitude = fields.Float('Latitud', related='silver_address_id.latitude', store=False)
    longitude = fields.Float('Latitud', related='silver_address_id.longitude', store=False)


    pri_onu_standar = fields.Char(string='PRI ONU Standar:')
    pri_onu_bridge = fields.Char(string='PRI ONU Bridge:')
    onu_ids_silver = fields.One2many('silver.onu.line', 'box_id', string='One serie')


    #contract_count = fields.Integer(string="Contratos", compute='_compute_contract_count')
 


    @api.model
    def action_unlink_from_node(self):
        self.ensure_one()
        self.write({'node_id': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_create_contract(self):
        self.ensure_one()
        return {
            'name': _('Crear Contrato'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.contract',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_box_id': self.id,
            }
        }

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



    def name_get(self):
        """
        Método estándar de Odoo para obtener el nombre a mostrar.
        Aquí manejamos el contexto para mostrar las coordenadas.
        """
        result = []
        for rec in self:

            name = self.get_name()


            # Si no hay datos de dirección legible, usamos el display_name
            if not name:
                name = rec.display_name
            result.append((rec.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        nodes = self.search(domain + args, limit=limit)
        return nodes.name_get()