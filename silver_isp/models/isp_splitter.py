from odoo import models, fields

class IspSplitter(models.Model):
    _name = 'isp.splitter'
    _description = 'Splitter de Conexion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Splitter')
    name_sppliter = fields.Char(string='Nombre')
    capacity_splitter = fields.Selection([], string='Capacidad')
    port_splitter = fields.Char(string='Puerto Splitter Primario')
    type_splitter = fields.Selection([('1', 'Primario'), ('2', 'Secundario')], string='Tipo')
    splitter_id = fields.Many2one('isp.splitter', string='Spliter Principal')
    olt_card_port_id = fields.Many2one('isp.olt.card.port', string='Puerto Tarjeta OLT')
    sppliter_latitude = fields.Float(string='Customer Latitude', digits=(16, 7))
    sppliter_longitude = fields.Float(string='Customer Longitude', digits=(16, 7))
    date_localization = fields.Date(string='Actualizado el:')
    box_count = fields.Integer(string='Conteo Cajas', compute='_compute_box_count')
    contracts_count = fields.Integer(string='Conteo Cajas', compute='_compute_contracts_count')

    def _compute_box_count(self):
        self.box_count = 0

    def _compute_contracts_count(self):
        self.contracts_count = 0

    def create_box(self):
        pass
