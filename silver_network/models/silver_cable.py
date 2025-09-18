# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverCable(models.Model):
    _name = 'silver.cable'
    _description = 'Network Cable'
    #_table = 'isp_cable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'silver.asset': 'asset_id'}

    asset_id = fields.Many2one('silver.asset', string='Asset', required=True, ondelete="cascade")

    cable_type = fields.Selection([
        ('fiber', 'Fiber Optic'),
        ('coaxial', 'Coaxial'),
        ('twisted_pair', 'Twisted Pair'),
        ('other', 'Other')
    ], string='Cable Type', default='fiber')

    line_string_wkt = fields.Char(string='Cable', related='asset_id.line_string_wkt', readonly=False)

    color = fields.Char(string="Color", related='asset_id.color',  readonly=False)

    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='cable',
        store=True,
        readonly=False
    )
