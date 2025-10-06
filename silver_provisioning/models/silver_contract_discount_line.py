# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import math
from odoo.exceptions import UserError

class SilverContractDiscountLine(models.Model):
    _inherit = 'silver.contract.discount.line'

    product_id = fields.Many2one('product.product', string='Producto/Servicio', required=True)

