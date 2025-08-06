from odoo import models, fields

class IspOltCard(models.Model):
    _name = 'isp.olt.card'
    _description = 'Tarjeta de Equipo OLT'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre Tarjeta')
    num_card = fields.Integer(string='Numero Slot')
    port_card = fields.Selection([], string='Cantidad Puertos')
    olt_id = fields.Many2one('isp.olt', string='OLT')
    type_access_net = fields.Selection([], string='Tipo')
    dhcp_custom_server = fields.Char(string='DHCP Leases')
    ip_address_line_ids = fields.One2many('isp.ip.address.line', 'card_id', string='Direcciones IP')
    ip_address_ids = fields.One2many('isp.ip.address', 'card_id', string='Direcciones IP')
    olt_card_port_count = fields.Integer(string='Conteo Slot OLT', compute='_compute_olt_card_port_count')
    contracts_card_count = fields.Integer(string='Conteo Tarjetas Olt', compute='_compute_contracts_card_count')

    def _compute_olt_card_port_count(self):
        self.olt_card_port_count = 0

    def _compute_contracts_card_count(self):
        self.contracts_card_count = 0

    def create_olt_card_port(self):
        pass
