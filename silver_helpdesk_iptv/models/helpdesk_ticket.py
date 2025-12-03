# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # IPTV Fields
    state_service_ott = fields.Selection(related='contract_id.state_service_ott', string="Estado Servicio OTT", readonly=True)
    
    # Flags
    subscription_iptv = fields.Boolean(related='contract_id.subscription_iptv', string="Suscripción IPTV", readonly=True)
    for_promotion_iptv = fields.Boolean(related='contract_id.for_promotion_iptv', string="Para Promoción IPTV", readonly=True)
    finish_promotion_iptv = fields.Boolean(related='contract_id.finish_promotion_iptv', string="Fin Promoción", readonly=True)
    
    # Promotion Info
    product_promotion_iptv_id = fields.Many2one(related='contract_id.product_promotion_iptv_id', string="Producto Promoción IPTV", readonly=True)
    date_init_promotion_iptv = fields.Date(related='contract_id.date_init_promotion_iptv', string="Fecha Inicio Promoción", readonly=True)
    date_finish_promotion_iptv = fields.Date(related='contract_id.date_finish_promotion_iptv', string="Fecha Fin Promoción", readonly=True)
    
    # Change / Add Plan
    product_iptv_add_id = fields.Many2one('product.product', string="Plan IPTV (Agregar)")
    contract_line_iptv_id = fields.Many2one('silver.contract.line', string="Línea IPTV Actual")
    product_iptv_id_old = fields.Many2one('product.product', string="Producto IPTV Anterior")
    product_iptv_id = fields.Many2one('product.product', string="Producto IPTV Nuevo")
    
    is_delete_product_iptv = fields.Boolean(string="Eliminar Producto IPTV")
    
    state_service_ott_related = fields.Selection(related='state_service_ott', string="Estado Servicio OTT (Related)")
    
    equipments_ott_ids = fields.Many2many('product.product', string="Equipos OTT", related='contract_id.equipments_ott_ids')
    assigned_equipments = fields.Char(string="Equipos Asignados", related='contract_id.assigned_equipments')
    
    # Actions placeholders
    def action_actiavte_iptv(self):
        pass
    def action_suscription_iptv(self):
        pass
    def action_add_plan_iptv_id(self):
        pass
    def action_change_product_iptv_id(self):
        pass
    def action_delete_service(self):
        pass
