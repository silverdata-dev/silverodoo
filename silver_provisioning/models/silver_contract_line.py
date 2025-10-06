# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SilverContractLine(models.Model):
    _inherit = 'silver.contract.line'


    product_id = fields.Many2one('product.product', string='Producto/Servicio', required=True)



    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.get_product_multiline_description_sale()
            self.price_unit = self.product_id.list_price


