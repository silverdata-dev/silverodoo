# -*- coding: utf-8 -*-

from odoo import models, fields

class HelpdeskStockLine(models.Model):
    _name = 'helpdesk.stock.line'
    _description = 'Línea de Materiales en Ticket'

    helpdesk_id = fields.Many2one('helpdesk.ticket', string="Ticket")
    product_id = fields.Many2one('product.product', string="Producto", required=True)
    qty_stock = fields.Float(string="Cantidad", default=1.0)
    qty_covered_stock = fields.Float(string="Cant. Cubierta")
    qty_extra_stock = fields.Float(string="Cant. Extra")
    
    lot_id = fields.Many2one('stock.lot', string="Lote/Serial")
    is_done = fields.Boolean(string="Realizado")
    is_invoice_covered = fields.Boolean(string="Facturado")
    is_promotion = fields.Boolean(string="Promoción")
    is_extra_material_line = fields.Boolean(string="Es Material Extra")
    is_remove_materials = fields.Boolean(string="Remover")
