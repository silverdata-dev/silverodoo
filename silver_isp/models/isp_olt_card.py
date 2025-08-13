from odoo import models, fields

class IspOltCard(models.Model):
    _name = 'isp.olt.card'
    _description = 'Tarjeta de Equipo OLT'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre Tarjeta')
    num_card = fields.Integer(string='Numero Slot')
    port_card = fields.Selection([], string='Cantidad Puertos')
    olt_id = fields.Many2one('isp.olt', string='OLT')
    type_access_net = fields.Selection(
        [('inactive', 'Inactivo'), ('dhcp', 'DHCP Leases'), ('manual', 'IP Asignada manualmente'),
         ('system', 'IP Asignada por el sistema')], default='inactive', string='Tipo Acceso', required=True)

    dhcp_custom_server = fields.Char(string='DHCP Leases')
    ip_address_line_ids = fields.One2many('isp.ip.address.line', 'card_id', string='Direcciones IP')
    ip_address_ids = fields.One2many('isp.ip.address', 'card_id', string='Direcciones IP')
    olt_card_port_count = fields.Integer(string='Conteo Slot OLT', compute='_compute_olt_card_port_count')
    contracts_card_count = fields.Integer(string='Conteo Tarjetas Olt', compute='_compute_contracts_card_count')

    def _compute_olt_card_port_count(self):
        for record in self:
            record.olt_card_port_count = self.env['isp.olt.card.port'].search_count([('olt_card_id', '=', record.id)])

    def _compute_contracts_card_count(self):
        for record in self:
            record.contracts_card_count = self.env['isp.contract'].search_count([('olt_card_id', '=', record.id)])

    def create_olt_card_port(self):
        self.ensure_one()
        ports_to_create = []
        for i in range(self.num_ports):
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
