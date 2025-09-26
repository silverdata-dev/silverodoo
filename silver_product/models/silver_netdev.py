# -*- coding: utf-8 -*-

from odoo import models, fields

class SilverNetdev(models.Model):
    _inherit = 'silver.netdev'

    stock_lot_id = fields.Many2one(
        'stock.lot',
        string='Equipo (Serie/Lote)',
        help="Vincula este dispositivo de red a un equipo específico con número de serie/lote."
    )