# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductBrand(models.Model):
    _name = 'product.brand'

    #_inherit = 'product.brand'
    name = fields.Char('Name')
    description = fields.Text('Description')
    partner_ids = fields.Many2many('res.partner', string='Proveedores')
    logo = fields.Binary(string='Imagen')



    product_ids = fields.One2many("product.template", "brand_id", string='Productos')

   # model_ids = fields.One2many("silver.hardware.model", "brand_id", string='Modelos')