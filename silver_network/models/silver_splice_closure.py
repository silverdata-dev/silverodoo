# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverSpliceClosure(models.Model):
    _name = 'silver.splice.closure'
    #_table = 'isp_splice_closure'
    _description = 'Splice Closure (Manga)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre")

    code = fields.Char(string="Código")
    node_id = fields.Many2one('silver.node', string='Nodo')

    zone_id = fields.Many2one('silver.zone', string="Zona")

    silver_address_id = fields.Many2one('silver.address', string='Dirección')


    latitude = fields.Float(string='Latitud', digits=(10, 7), related='silver_address_id.latitude')
    longitude = fields.Float(string='Longitud', digits=(10, 7), related='silver_address_id.longitude')

    notes = fields.Text(string="Notas")



    closure_type = fields.Selection([
        ('dome', 'Dome'),
        ('inline', 'Inline'),
        ('other', 'Other')
    ], string='Closure Type', default='other')

    capacity = fields.Integer(string='Splice Capacity')



