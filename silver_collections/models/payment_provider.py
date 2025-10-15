# -*- coding: utf-8 -*-
from odoo import models, fields

class PaymentProvider(models.Model):
    _name = 'payment.provider'
    _description = 'Proveedor de Servicios de Pago'

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Código", required=True, help="Código técnico para identificar este proveedor.")
    state = fields.Selection([
        ('disabled', 'Deshabilitado'),
        ('test', 'Modo de Prueba'),
        ('production', 'Producción'),
    ], string="Estado", default='disabled', required=True)

    api_url = fields.Char(string="URL del API")
    api_token = fields.Char(string="Token/Clave API", password=True)

    journal_id = fields.Many2one(
        'account.journal',
        string="Diario de Pago",
        domain="[('type', 'in', ('bank', 'cash'))]",
        help="El diario contable donde se registrarán los pagos de este proveedor."
    )

_sql_constraints = [
    ('code_uniq', 'unique (code)', '¡El código del proveedor debe ser único!')
]
