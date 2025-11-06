# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverServiceType(models.Model):
    _name = 'silver.service.type'
    _description = 'Tipo de Servicio para Contratos ISP'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Descripción')
