from odoo import models, fields, api

class IspOltCard(models.Model):
    _name = 'isp.olt.card'
    _description = 'Tarjeta de Equipo OLT'
    _inherit = ['isp.netdev', 'mail.thread', 'mail.activity.mixin']

    """name = fields.Char(string='Nombre Tarjeta', readonly=True, copy=False, default='New')
    num_card = fields.Integer(string='Numero Slot')
    port_card = fields.Selection([('1','1'),('2','2'),('4','4'),('8','8'),('16','16')], string='Cantidad Puertos')
    olt_id = fields.Many2one('isp.olt', string='OLT', required=True, ondelete='cascade')
    type_access_net = fields.Selection(
        [('inactive', 'Inactivo'), ('dhcp', 'DHCP Leases'), ('manual', 'IP Asignada manualmente'),
         ('system', 'IP Asignada por el sistema')], default='inactive', string='Tipo Acceso', required=True)

    dhcp_custom_server = fields.Char(string='DHCP Leases')
    ip_address_line_ids = fields.One2many('isp.ip.address.line', 'card_id', string='Direcciones IP')
    ip_address_ids = fields.One2many('isp.ip.address', 'card_id', string='Direcciones IP')
    olt_card_port_count = fields.Integer(string='Conteo Slot OLT', compute='_compute_olt_card_port_count')
    contracts_card_count = fields.Integer(string='Conteo Tarjetas Olt', compute='_compute_contracts_card_count')
    """

    olt_id = fields.Many2one('isp.olt', string='OLT', required=True)
    gateway = fields.Many2one('isp.ip.address', string='Gateway')
    
    # --- Campos de Acceso y Configuración ---
    num_card = fields.Integer(string='Número Slot')
    poolip = fields.Char(string='Poolip')
    dhcp_custom_server = fields.Char(string='DHCP Leases')
    
    # --- Opciones de Configuración (Booleanos y Selección) ---
    is_generate = fields.Boolean(string='Generado?')
    port_card = fields.Selection([
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Cantidad de Puertos')
    type_access_net = fields.Selection([
        ('wired', 'Cableado'),
        ('wireless', 'Inalámbrico')
    ], string='Tipo de Acceso')
    
    # --- Campos de Lectura (Computados) ---
    display_name = fields.Char(string='Display Name', compute='_compute_display_name')
    contracts_card_count = fields.Integer(string='Conteo Tarjetas Olt', compute='_compute_counts')
    olt_card_port_count = fields.Integer(string='Conteo Puertos', compute='_compute_counts')
    
    # --- Métodos Computados ---
    @api.depends('name', 'olt_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.olt_id.name} / {record.name}" if record.olt_id else record.name

    @api.model
    def create(self, vals):
        if vals.get('olt_id'):
            olt = self.env['isp.olt'].browse(vals['olt_id'])
            if olt.exists():
                card_count = self.search_count([('olt_id', '=', olt.id)])
                vals['name'] = f"{olt.name}/CARD{card_count + 1}"
        return super(IspOltCard, self).create(vals)

    def write(self, vals):
        # If the olt_id is being changed, we need to rename the card
        if 'olt_id' in vals:
            new_olt = self.env['isp.olt'].browse(vals['olt_id'])
            if new_olt.exists():
                for record in self:
                    # We need to count the cards in the new OLT to get the next number
                    card_count = self.search_count([('olt_id', '=', new_olt.id)])
                    record.name = f"{new_olt.name}/CARD{card_count + 1}"
        return super(IspOltCard, self).write(vals)

    def _compute_olt_card_port_count(self):
        for record in self:
            record.olt_card_port_count = self.env['isp.olt.card.port'].search_count([('olt_card_id', '=', record.id)])

    def _compute_contracts_card_count(self):
        for record in self:
            record.contracts_card_count = self.env['isp.contract'].search_count([('olt_card_id', '=', record.id)])

    def create_olt_card_port(self):
        self.ensure_one()
        ports_to_create = []
        for i in range(int(self.port_card)):
            ports_to_create.append({
                'name': f"{self.name}/port/{i+1}",
                'olt_card_id': self.id,
            })
        self.env['isp.olt.card.port'].create(ports_to_create)
        return {
            'name': 'Puertos de Tarjeta OLT',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.olt.card.port',
            'view_mode': 'tree,form',
            'domain': [('olt_card_id', '=', self.id)],
            'target': 'current',
        }

    def action_view_olt_card_ports(self):
        self.ensure_one()
        return {
            'name': 'Puertos OLT',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.olt.card.port',
            'view_mode': 'tree,form',
            'domain': [('olt_card_id', '=', self.id)],
            'context': {'default_olt_card_id': self.id},
            'target': 'current',
        }

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': 'Contratos',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.contract',
            'view_mode': 'tree,form',
            'domain': [('olt_card_id', '=', self.id)],
            'context': {'default_olt_card_id': self.id},
            'target': 'current',
        }
