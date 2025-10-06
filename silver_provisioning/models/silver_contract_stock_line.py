# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverContractStockLine(models.Model):
    _inherit = 'silver.contract.stock.line'

    product_id = fields.Many2one('product.product', string='Producto/Equipo', required=True)

    lot_id = fields.Many2one('stock.lot', string="Número de Serie") #, domain="[ ('product_id', '=', product_id)]")