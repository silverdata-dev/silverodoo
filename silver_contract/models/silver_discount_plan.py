# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverDiscountPlan(models.Model):
    _name = 'silver.discount.plan'
    _description = 'Plan de Descuento para Contratos ISP'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    active = fields.Boolean(string='Activo', default=True)
    description = fields.Text(string='Descripción')
    
    discount_type = fields.Selection([
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto Fijo')
    ], string='Tipo de Descuento', required=True, default='percentage')

    amount = fields.Float(string='Monto/Porcentaje', required=True)

