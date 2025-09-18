# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SilverContractLine(models.Model):
    _name = 'silver.contract.line'
    _description = 'Línea de Contrato de Servicio ISP'

    contract_id = fields.Many2one('silver.contract', string='Contrato', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Producto/Servicio', required=True)
    line_type = fields.Selection([
        ('recurring', 'Recurrente'),
        ('one_time', 'Cargo Único')
    ], string="Tipo de Línea", default='recurring', required=True)
    
    name = fields.Text(string='Descripción', required=True)
    quantity = fields.Float(string='Cantidad', required=True, default=1.0)
    price_unit = fields.Float(string='Precio Unitario', required=True)
    
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal', store=True)
    #currency_id = fields.Many2one(related='contract_id.partner_id.currency_id', store=True)
    currency_id = fields.Many2one('res.currency')


    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.get_product_multiline_description_sale()
            self.price_unit = self.product_id.list_price
