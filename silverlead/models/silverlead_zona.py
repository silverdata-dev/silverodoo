# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverleadZona(models.Model):
    _name = 'silverlead.zona'
    _description = 'Zona de Silverlead'

    name = fields.Char('Nombre', required=True, index=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'El nombre de la zona debe ser único.')
    ]
