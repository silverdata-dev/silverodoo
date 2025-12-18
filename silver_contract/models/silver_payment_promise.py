# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverPaymentPromise(models.Model):
    _name = 'silver.payment.promise'
    _description = 'Promesa de Pago de Cliente'
    _order = 'promise_date desc'

    name = fields.Char(string='Descripción', required=True)
    contract_id = fields.Many2one('silver.contract', string='Contrato', required=True, ondelete='cascade')
    #invoice_id = fields.Many2one('account.move', string='Factura Afectada')
    amount = fields.Monetary(string='Monto Prometido', currency_field='currency_id')
    #currency_id = fields.Many2one(related='contract_id.partner_id.currency_id')
    currency_id = fields.Many2one('res.currency')

    promise_date = fields.Date(string='Fecha Prometida', required=True)
    state = fields.Selection([('draft', 'Borrador'), ('kept', 'Cumplida'), ('broken', 'Incumplida')], string='Estado', default='draft')
