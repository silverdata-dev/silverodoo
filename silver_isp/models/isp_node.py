from odoo import models, fields, api

class IspNode(models.Model):
    _name = 'isp.node'
    _description = 'Nodo ISP'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre del Nodo', required=True)
    code = fields.Char(string='Código del Nodo', required=True)
    
    street = fields.Char(string='Calle')
    street2 = fields.Char(string='Calle 2')
    zip = fields.Char(string='Código Postal')
    state_id = fields.Many2one('res.country.state', string='Estado')
    country_id = fields.Many2one('res.country', string='País')
    phone = fields.Char(string='Teléfono')

    node_latitude = fields.Float(string='Latitud', digits=(16, 7))
    node_longitude = fields.Float(string='Longitud', digits=(16, 7))
    date_localization = fields.Date(string='Fecha de Geolocalización')
    distance = fields.Float(string='Distancia')

    journal_id = fields.Many2one('account.journal', string='Diario')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica de Ingresos')
    account_cost_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica de Costos')

    core_count = fields.Integer(string='Equipos Core', compute='_compute_counts')
    support_ticket_count = fields.Integer(string='Tickets', compute='_compute_counts')
    stock_picking_count = fields.Integer(string='Movimientos', compute='_compute_counts')
    olt_count = fields.Integer(string='Equipos OLT', compute='_compute_counts')

    def _compute_counts(self):
        for record in self:
            # Logica para contar los equipos, tickets, etc.
            record.core_count = 0
            record.support_ticket_count = 0
            record.stock_picking_count = 0
            record.olt_count = 0

    def create_core(self):
        # Lógica para crear un equipo core
        pass

    def action_create_ticket_node(self):
        # Lógica para crear un ticket
        pass

    def create_olt(self):
        # Lógica para crear un equipo OLT
        pass

    def action_search_view_olts(self):
        # Lógica para buscar y mostrar OLTs
        pass
