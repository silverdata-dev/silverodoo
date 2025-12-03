# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # --- Contract Integration ---
    contract_id = fields.Many2one('silver.contract', string='Contrato', domain="[('partner_id', '=', partner_id)]")
    
    period = fields.Many2one(related='contract_id.contract_term_id', string="Período", readonly=True)
    address_contract = fields.Char(related='contract_id.silver_address_id.display_name', string="Dirección Contrato", readonly=True)
    phone_contract = fields.Char(related='contract_id.phone', string="Teléfono Contrato", readonly=True)
    
    address_ref_contract = fields.Char(string="Referencia Dirección")
    address_ref_contract_new = fields.Char(string="Nueva Referencia Dirección")

    state_service = fields.Selection(related='contract_id.state_service', string="Estado Servicio", readonly=True)
    
    # --- Logic / View Control Flags (Contract) ---
    code_category_id = fields.Char(related='ticket_type_id.code', string="Código Categoría")
    
    is_invoice_service = fields.Boolean(string="Facturar Servicios")
    
    # Commercial Process Flags
    is_change_product_id = fields.Boolean(string="Cambio de Plan")
    is_change_partner = fields.Boolean(string="Cambio de Titular")
    is_change_suspension = fields.Boolean(string="Cambio de Suspensión")
    is_change_date = fields.Boolean(string="Cambio de Fecha")
    is_change_payment_method = fields.Boolean(string="Cambio de Forma de Pago")
    is_change_cuttoff_date = fields.Boolean(string="Cambio de Ciclo")
    
    # Solution
    solution_id = fields.Many2one('silver.ticket.solution', string="Solución")
    solution = fields.Text(string="Detalle Solución")

class SilverTicketSolution(models.Model):
    _name = 'silver.ticket.solution'
    _description = 'Solución de Ticket'
    
    name = fields.Char(string="Solución", required=True)
    code = fields.Char(string="Código")