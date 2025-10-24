# -*- coding: utf-8 -*-
from odoo import models, fields

class StockLot(models.Model):
    _inherit = 'stock.lot'

    external_equipment = fields.Boolean(string='Equipo externo')
    serial_number = fields.Char(string='Número Serial', related='name')
    applied_accounting_cost = fields.Boolean(string='Costo Contable Aplicado')

    software_version  = fields.Char(string='Versión software')
    firmware_version = fields.Char(string='Firmware Version', readonly=False)


