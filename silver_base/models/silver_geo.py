# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverMunicipality(models.Model):
    _name = 'silver.municipality'
    _description = 'Municipalidad'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    state_id = fields.Many2one('res.country.state', string='State', required=True)

class SilverCity(models.Model):
    _name = 'silver.city'
    _description = 'Ciudad'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    municipality_id = fields.Many2one('silver.municipality', string='Municipality', required=True)

class SilverParish(models.Model):
    _name = 'silver.parish'
    _description = 'Parroquia'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    city_id = fields.Many2one('silver.city', string='City', required=True)
