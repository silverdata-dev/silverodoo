# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    silver_address_id = fields.Many2one('silver.address', string='Dirección')

