# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SilverTicket(models.Model):
    _name = 'silver.ticket'
    _inherit = 'helpdesk.ticket'

    ticket_type = fields.Selection([
        ('failure', 'Caída de Conexión'),
        ('slow_speed', 'Lentitud'),
        ('billing', 'Facturación'),
        ('installation', 'Instalación'),
        ('other', 'Otro'),
    ], string='Tipo de Ticket', default='failure', required=True)

    contract_id = fields.Many2one('silver.contract', string='Contrato')
    partner_id = fields.Many2one(related='contract_id.partner_id', store=True)
