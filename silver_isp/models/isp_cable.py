# -*- coding: utf-8 -*-
from odoo import models, fields

class IspCable(models.Model):
    _name = 'isp.cable'
    _description = 'Network Cable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'isp.asset': 'asset_id'}

    asset_id = fields.Many2one('isp.asset', string='Asset', required=True, ondelete="cascade")

    cable_type = fields.Selection([
        ('fiber', 'Fiber Optic'),
        ('coaxial', 'Coaxial'),
        ('twisted_pair', 'Twisted Pair'),
        ('other', 'Other')
    ], string='Cable Type', default='fiber')

    fiber_count = fields.Integer(string='Fiber Count')
    length = fields.Float(string='Length (meters)')

    # This field will store the sequence of assets that form the cable's route
    route_asset_ids = fields.Many2many(
        'isp.asset',
        'isp_cable_asset_route_rel',
        'cable_id',
        'asset_id',
        string='Route'
    )

    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='cable',
        store=True,
        readonly=False
    )
