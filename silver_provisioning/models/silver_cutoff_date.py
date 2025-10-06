# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SilverCutoffDate(models.Model):
    _inherit = 'silver.cutoff.date'


    product_reconnection_id = fields.Many2one('product.product', string='Producto/Servicio Cortado')
    product_remove_reconnection_id = fields.Many2one('product.product', string='Producto/Servicio Lista de Retiro')

