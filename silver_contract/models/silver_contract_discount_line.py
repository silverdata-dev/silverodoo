# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverContractDiscountLine(models.Model):
    _name = 'silver.contract.discount.line'
    _description = 'Línea de Descuento Aplicado en Contrato'
    _order = 'apply_date desc'

    product_id = fields.Many2one('product.product', string='Producto/Servicio', required=True)

    contract_id = fields.Many2one('silver.contract', string='Contrato', required=True, ondelete='cascade')
    discount_plan_id = fields.Many2one('silver.discount.plan', string='Plan de Descuento')
    
    description = fields.Char(string='Descripción', required=True)
    amount = fields.Float(string='Monto Descontado')
    apply_date = fields.Date(string='Fecha de Aplicación', default=fields.Date.context_today)
    product_id = fields.Many2one('product.product', string='Producto')

