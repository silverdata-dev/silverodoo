# -*- coding: utf-8 -*-
from odoo import models, fields

class IspReferredContact(models.Model):
    _name = 'isp.referred.contact'
    _description = 'Contacto Referido por Cliente'
    _order = 'referred_date desc'

    name = fields.Char(string='Nombre del Referido', required=True)
    phone = fields.Char(string='Teléfono')
    email = fields.Char(string='Email')
    
    contract_id = fields.Many2one('isp.contract', string='Contrato que Refiere', required=True, ondelete='cascade')
    referred_date = fields.Date(string='Fecha de Referencia', default=fields.Date.context_today)
    
    state = fields.Selection([
        ('new', 'Nuevo'),
        ('contacted', 'Contactado'),
        ('converted', 'Convertido'),
        ('lost', 'Perdido')
    ], string='Estado', default='new')
    
    converted_contract_id = fields.Many2one('isp.contract', string='Contrato Convertido', help="El contrato que se creó si el referido se convirtió en cliente.")
