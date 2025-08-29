# -*- coding: utf-8 -*-
from odoo import models, fields

class IspSpliceClosure(models.Model):
    _name = 'isp.splice.closure'
    _description = 'Splice Closure (Manga)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'isp.asset': 'asset_id'}

    asset_id = fields.Many2one('isp.asset', string='Asset', required=True, ondelete="cascade")

    name = fields.Char(string="Nombre", related="asset_id.name", readonly=False)

    node_id = fields.Many2one('isp.node', string='Nodo')
    zone_id = fields.Many2one('isp.zone', string="Zona", related="asset_id.zone_id", readonly=False)
    


    closure_type = fields.Selection([
        ('dome', 'Dome'),
        ('inline', 'Inline'),
        ('other', 'Other')
    ], string='Closure Type', default='other')

    capacity = fields.Integer(string='Splice Capacity')

    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='manga',
        store=True,
        readonly=False
    )
