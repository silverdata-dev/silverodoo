# -*- coding: utf-8 -*-
from odoo import models, fields

class IspContractStockLine(models.Model):
    _name = 'isp.contract.stock.line'
    _description = 'Línea de Material/Equipo Asignado a Contrato'

    contract_id = fields.Many2one('isp.contract', string='Contrato', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Producto/Equipo', required=True)
    lot_id = fields.Many2one('stock.lot', string="Número de Serie", domain="[ ('product_id', '=', product_id)]")
    quantity = fields.Float(string='Cantidad', default=1.0, required=True)
    assignment_date = fields.Date(string='Fecha de Asignación', default=fields.Date.context_today)
    state = fields.Selection([('assigned', 'Asignado'), ('returned', 'Devuelto')], string="Estado", default='assigned')
