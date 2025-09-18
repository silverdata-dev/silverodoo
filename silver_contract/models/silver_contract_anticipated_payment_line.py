# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverContractAnticipatedPaymentLine(models.Model):
    _name = 'silver.contract.anticipated.payment.line'
    _description = 'Línea de Pago Anticipado en Contrato'
    _order = 'date desc'


    contract_id = fields.Many2one('silver.contract', string='Contrato', required=True, ondelete='cascade')
    payment_id = fields.Many2one('account.payment', string='Pago Asociado')
    amount = fields.Monetary(string='Monto Anticipado', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency')
    date = fields.Date(string='Fecha', required=True, default=fields.Date.context_today)
    description = fields.Text(string='Descripción')



    #@api.depends('contract_id')
    #def _compute_value(self):
#        for quant in self:
#            quant.currency_id = quant.company_id.currency_id


