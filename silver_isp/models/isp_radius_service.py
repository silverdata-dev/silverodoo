# -*- coding: utf-8 -*-

from odoo import models, fields

class IspRadiusService(models.Model):
    _name = 'isp.radius.service'
    _description = 'MikroTik Radius Service'

    name = fields.Char(string='Service Name', required=True)
    description = fields.Text(string='Description')