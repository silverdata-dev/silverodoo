# -*- coding: utf-8 -*-
from odoo import models, fields

class IspPaymentType(models.Model):
    _name = 'isp.payment.type'
    _description = 'Forma de Pago para Contratos ISP'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
