# -*- coding: utf-8 -*-
from odoo import models, fields

class IspContractAnticipatedPaymentLine(models.Model):
    _name = 'isp.contract.anticipated.payment.line'
    _description = 'Línea de Pago Anticipado en Contrato'
    _order = 'date desc'

    contract_id = fields.Many2one('isp.contract', string='Contrato', required=True, ondelete='cascade')
    payment_id = fields.Many2one('account.payment', string='Pago Asociado')
    amount = fields.Monetary(string='Monto Anticipado', currency_field='currency_id')
    currency_id = fields.Many2one(related='contract_id.partner_id.currency_id')
    date = fields.Date(string='Fecha', required=True, default=fields.Date.context_today)
    description = fields.Text(string='Descripción')
