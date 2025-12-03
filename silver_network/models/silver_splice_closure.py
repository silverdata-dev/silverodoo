# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverSpliceClosure(models.Model):
    _name = 'silver.splice.closure'
    #_table = 'isp_splice_closure'
    _description = 'Splice Closure (Manga)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'silver.asset': 'asset_id'}

    asset_id = fields.Many2one('silver.asset', string='Asset', required=True, ondelete="cascade")

    name = fields.Char(string="Nombre", related="asset_id.name", readonly=False)


    node_id = fields.Many2one('silver.node', string='Nodo')

    zone_id = fields.Many2one('silver.zone', string="Zona", related="asset_id.zone_id", readonly=False)

    silver_address_id = fields.Many2one('silver.address', string='Dirección', related="asset_id.silver_address_id")



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


