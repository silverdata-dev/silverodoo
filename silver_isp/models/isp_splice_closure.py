# -*- coding: utf-8 -*-
from odoo import models, fields

class IspSpliceClosure(models.Model):
    _name = 'isp.splice.closure'
    _description = 'Splice Closure (Manga)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'isp.asset': 'asset_id'}

    asset_id = fields.Many2one('isp.asset', string='Asset', required=True, ondelete="cascade")

    closure_type = fields.Selection([
        ('dome', 'Dome'),
        ('inline', 'Inline'),
        ('other', 'Other')
    ], string='Closure Type', default='other')

    capacity = fields.Integer(string='Splice Capacity')

    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='splice_closure',
        store=True,
        readonly=False
    )
