# -*- coding: utf-8 -*-
from odoo import models, fields

class ResCountryCity(models.Model):
    _inherit = 'res.country.city'

    latitude = fields.Float(string='Latitud', digits=(10, 7))
    longitude = fields.Float(string='Longitud', digits=(10, 7))
