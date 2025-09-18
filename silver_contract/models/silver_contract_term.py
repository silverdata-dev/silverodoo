# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverContractTerm(models.Model):
    _name = 'silver.contract.term'
    _description = 'Período de Permanencia para Contratos ISP'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    months = fields.Integer(string='Duración en Meses')
    description = fields.Text(string='Descripción')
