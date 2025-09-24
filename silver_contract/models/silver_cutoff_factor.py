# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverCutoffFactor(models.Model):
    _name = 'silver.cutoff.factor'
    _description = 'Factor de Corte para Periodo de Consumo'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
