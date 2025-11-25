# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SilverHardwareModel(models.Model):
    _name = 'silver.hardware.model'
    _description = 'Hardware Model'

    name = fields.Char(string='Name', required=True)
    brand_id = fields.Many2one('product.brand', string='Brand')
    onu_profile_id = fields.Many2one('silver.onu.profile', string='ONU Profile')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    etype = fields.Selection([('core', 'Core'), ('olt', 'OLT'), ('onu', 'ONU'), ('ap', 'AP'), ('ecp', 'ECP'), ('splitter', 'Splitter'), ('box', 'NAP'), ], string='Tipo de equipo')
    manual = fields.Boolean(string='Configuración Manual')

    _sql_constraints = [
        ('name_brand_uniq', 'unique (name, brand_id)', 'The model name must be unique per brand!')
    ]
