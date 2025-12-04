from odoo import models, fields, api

class SilverOltCard(models.Model):
    _name = 'silver.olt.card'
    _description = 'Tarjeta de Equipo OLT'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    #_table = 'isp_olt_card'


    olt_id = fields.Many2one('silver.olt', string='OLT', required=True)

    port_ids = fields.One2many('silver.olt.card.port', 'olt_card_id', string='Puertos')

    name = fields.Char(string='Nombre')

    # --- Campos de Acceso y Configuración ---
    num_card = fields.Integer(string='Número Slot')
    poolip = fields.Char(string='Poolip')
    dhcp_custom_server = fields.Char(string='DHCP Leases')

    port_card = fields.Selection([
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Cantidad de Puertos')

    #contracts_card_count = fields.Integer(string='Conteo Tarjetas Olt', compute='_compute_counts')

    olt_card_port_count = fields.Integer(string='Conteo Puertos', compute='_compute_olt_card_port_count')
    

    @api.model
    def create(self, vals):
        if vals.get('olt_id'):
            olt = self.env['silver.olt'].browse(vals['olt_id'])
            if olt.exists():
                card_count = self.search_count([('olt_id', '=', olt.id)])
                vals['name'] = f"{olt.name}/C{card_count}"
        return super(SilverOltCard, self).create(vals)

    def write(self, vals):
        # If the olt_id is being changed, we need to rename the card
        if 'olt_id' in vals:
            new_olt = self.env['silver.olt'].browse(vals['olt_id'])
            if new_olt.exists():
                for record in self:
                    # We need to count the cards in the new OLT to get the next number
                    card_count = self.search_count([('olt_id', '=', new_olt.id)])
                    record.name = f"{new_olt.name}/C{card_count}"
        return super(SilverOltCard, self).write(vals)

    def _compute_olt_card_port_count(self):
        for record in self:
            record.olt_card_port_count = self.env['silver.olt.card.port'].search_count([('olt_card_id', '=', record.id)])

    def create_olt_card_port(self):
        self.ensure_one()
        ports_to_create = []
        for i in range(int(self.port_card)):
            ports_to_create.append({
                'name': f"{self.name}/P{i+1}",
                'olt_card_id': self.id,
            })
        self.env['silver.olt.card.port'].create(ports_to_create)
        return {
            'name': 'Puertos de Tarjeta OLT',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.olt.card.port',
            'view_mode': 'tree,form',
            'domain': [('olt_card_id', '=', self.id)],
            'target': 'current',
        }

    def action_view_olt_card_ports(self):
        self.ensure_one()
        return {
            'name': 'Puertos OLT',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.olt.card.port',
            'view_mode': 'tree,form',
            'domain': [('olt_card_id', '=', self.id)],
            'context': {'default_olt_card_id': self.id},
            'target': 'current',
        }

