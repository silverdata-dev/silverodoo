# -*- coding: utf-8 -*-

from odoo import models, fields

class SilverRadiusService(models.Model):
    _name = 'silver.radius.service'
    _description = 'MikroTik Radius Service'

    name = fields.Char(string='Service Name', required=True)
    description = fields.Text(string='Description')