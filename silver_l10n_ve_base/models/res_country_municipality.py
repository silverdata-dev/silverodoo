# -*- coding: utf-8 -*-
from odoo import models, fields

class ResCountryMunicipality(models.Model):
    _inherit = 'res.country.municipality'

    city_id = fields.Many2one('res.country.city', string='Ciudad')
