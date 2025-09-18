# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverPlanType(models.Model):
    _name = 'silver.plan.type'
    _description = 'Tipo de Plan para Contratos ISP'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
