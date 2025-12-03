# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    stock_line_ids = fields.One2many('helpdesk.stock.line', 'helpdesk_id', string="Materiales Asignados")
    
    # Alias or subsets of stock lines for specific views
    device_extra_line_ids = fields.One2many('helpdesk.stock.line', 'helpdesk_id', string="Equipos Extras", domain=[('is_extra_material_line', '=', True)])
    new_stock_equipment_line_ids = fields.One2many('helpdesk.stock.line', 'helpdesk_id', string="Nuevos Equipos Extras", context={'default_is_extra_material_line': True})
    helpdesk_stock_ids = fields.One2many('helpdesk.stock.line', 'helpdesk_id', string="Stock Lines") # Same relation
    
    stock_count = fields.Integer(compute='_compute_stock_count', string="Movimientos Stock")
    
    is_remove_extra_equipment = fields.Boolean(string="Remover Equipos Extras")
    is_change_stock_equipment = fields.Boolean(string="Cambio Equipos Stock")
    
    computed_domain_previous_lot = fields.Char(invisible=True)
    
    is_change_extra_equipment = fields.Boolean(string="¿Cambiar Equipos?")
    is_add_extra_equipment = fields.Boolean(string="¿Agregar Equipos?")
    
    previous_lot_id = fields.Many2one('stock.lot', string="Lote Anterior")
    new_lot_id = fields.Many2one('stock.lot', string="Lote Nuevo")
    
    is_invoice_materials = fields.Boolean(string="Facturar Materiales")
    is_egress = fields.Boolean(string="Egreso Realizado")
    
    # Synchronize fields from snippet
    synchronize_serial_onu = fields.Char()
    synchronize_model_onu_type_id = fields.Many2one('product.product')
    external_synchronize_serial_onu = fields.Char()
    external_synchronize_model_onu_id = fields.Many2one('product.product')

    def _compute_stock_count(self):
        for ticket in self:
            ticket.stock_count = 0 # Implement logic to count picking ids
    
    def action_open_stock_picking(self):
        pass # Implement action
        
    def action_invoice_ticket_materials(self):
        pass
        
    def action_move_done(self):
        pass
        
    def action_register_active(self):
        pass
    
    def action_remove_extra_equipment(self):
        pass
        
    def action_change_equipment_extra(self):
        pass
