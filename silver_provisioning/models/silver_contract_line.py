# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SilverContractLine(models.Model):
    _inherit = 'silver.contract.line'


    product_id = fields.Many2one('product.product', string='Producto/Servicio', required=True)

    linktype_id = fields.Many2one('silver.linktype', string="Tipo de Conexión",)


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.get_product_multiline_description_sale() or self.product_id.name
            self.price_unit = self.product_id.list_price


    @api.model
    def default_get(self, fields):
        # 1. Llamar al método base para obtener los defaults estándar
        res = super(SilverContractLine, self).default_get(fields)



        print(("defline", self.env.context, res, fields))

        return res