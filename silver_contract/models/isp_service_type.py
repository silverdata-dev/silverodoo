# -*- coding: utf-8 -*-
from odoo import models, fields

class IspServiceType(models.Model):
    _name = 'isp.service.type'
    _description = 'Tipo de Servicio para Contratos ISP'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
