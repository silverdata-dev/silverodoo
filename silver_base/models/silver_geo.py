# -*- coding: utf-8 -*-
from odoo import models, fields


class SilverCity(models.Model):
    _name = 'silver.city'
    _description = 'Ciudad'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    state_id = fields.Many2one('res.country.state', string='Estado', required=True)


class SilverMunicipality(models.Model):
    _name = 'silver.municipality'
    _description = 'Municipio'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    city_id = fields.Many2one('silver.city', string='Ciudad', required=True)

class SilverParish(models.Model):
    _name = 'silver.parish'
    _description = 'Parroquia'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    municipality_id = fields.Many2one('silver.municipality', string='Municipio', required=True)
