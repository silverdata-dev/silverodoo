# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverOltCardPort(models.Model):
    _inherit = 'silver.olt.card.port'
    _inherits = {'silver.access_point': 'access_point_id'}

    access_point_id = fields.Many2one(
        'silver.access_point', 
        string='Registro de Provisioning', 
        required=True, 
        ondelete='cascade',
        help="Registro de provisioning asociado a este Puerto OLT."
    )
