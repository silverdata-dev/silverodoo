# -*- coding: utf-8 -*-
from odoo import models, fields

class IspContractDiscountLine(models.Model):
    _name = 'isp.contract.discount.line'
    _description = 'Línea de Descuento Aplicado en Contrato'
    _order = 'apply_date desc'

    contract_id = fields.Many2one('isp.contract', string='Contrato', required=True, ondelete='cascade')
    discount_plan_id = fields.Many2one('isp.discount.plan', string='Plan de Descuento')
    
    description = fields.Char(string='Descripción', required=True)
    amount = fields.Float(string='Monto Descontado')
    apply_date = fields.Date(string='Fecha de Aplicación', default=fields.Date.context_today)

