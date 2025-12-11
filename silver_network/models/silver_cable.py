# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverCable(models.Model):
    _name = 'silver.cable'
    _description = 'Network Cable'
    #_table = 'isp_cable'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre")
    code = fields.Char(string="Código")
    cable_type = fields.Selection([
        ('fiber', 'Fiber Optic'),
        ('coaxial', 'Coaxial'),
        ('twisted_pair', 'Twisted Pair'),
        ('other', 'Other')
    ], string='Cable Type', default='fiber')

    line_string_wkt = fields.Char(string='Cable',  readonly=False)

    color = fields.Char(string="Color")
    notes = fields.Text(string="Notas")

    #silver_address_ids = fields.Many2many(comodel_name='silver.address', string='Dirección')
