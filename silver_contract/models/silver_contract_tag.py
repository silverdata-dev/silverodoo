# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverContractTag(models.Model):
    _name = 'silver.contract.tag'
    _description = 'Etiqueta para Contratos'
    _order = 'name'

    name = fields.Char(string='Nombre de la Etiqueta', required=True)
    color = fields.Integer(string='Color')
    is_technical = fields.Boolean(string='Es Etiqueta Técnica', help='Para diferenciar etiquetas administrativas (VIP, Moroso) de técnicas (Requiere Soporte, Equipo Antiguo).')
