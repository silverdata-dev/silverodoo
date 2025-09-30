# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverPaymentType(models.Model):
    _name = 'silver.payment.type'
    _description = 'Forma de Pago para Contratos ISP'
    _order = 'name'

    code = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
