# -*- coding: utf-8 -*-
from odoo import models, fields

class PaymentTransaction(models.Model):
    _name = 'payment.transaction'
    _description = 'Transacción de Pago'
    _order = 'create_date desc'

    reference = fields.Char(string="Referencia", required=True, readonly=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('payment.transaction'))
    provider_id = fields.Many2one('payment.provider', string="Proveedor", required=True, readonly=True)
    contract_id = fields.Many2one('silver.contract', string="Contrato", required=True, readonly=True)
    amount = fields.Monetary(string="Monto", required=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='contract_id.currency_id', readonly=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('pending', 'Pendiente'),
        ('done', 'Realizado'),
        ('failed', 'Fallido'),
        ('canceled', 'Cancelado'),
    ], string="Estado", default='draft', required=True, copy=False, tracking=True)

    provider_reference = fields.Char(string="Referencia del Proveedor", readonly=True, copy=False)
    raw_request = fields.Text(string="Petición a la API", readonly=True)
    raw_response = fields.Text(string="Respuesta de la API", readonly=True)
    payment_id = fields.Many2one('account.payment', string="Pago Relacionado", readonly=True, copy=False)
