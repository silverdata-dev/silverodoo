# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import math
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_silver_plan = fields.Boolean(string="Es un Plan ISP", help="Marcar si este producto es un plan de servicio para ISP.")