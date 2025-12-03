# -*- coding: utf-8 -*-

from odoo import models, fields

class ContractContract(models.Model):
    _inherit = 'silver.contract'

    state_service_ott = fields.Selection([
        ('inactive', 'Inactivo'), ('active', 'Activo'),
        ('suspended', 'Suspendido'), ('disabled', 'Cortado')
    ], string="Estado Servicio OTT", default='inactive')
    
    subscription_iptv = fields.Boolean(string="Suscripción IPTV")
    for_promotion_iptv = fields.Boolean(string="Para Promoción IPTV")
    product_promotion_iptv_id = fields.Many2one('product.product', string="Producto Promoción IPTV")
    date_init_promotion_iptv = fields.Date(string="Fecha Inicio Promoción")
    date_finish_promotion_iptv = fields.Date(string="Fecha Fin Promoción")
    finish_promotion_iptv = fields.Boolean(string="Fin Promoción")
    
    equipments_ott_ids = fields.Many2many('product.product', string="Equipos OTT") # Relation needs verification
    assigned_equipments = fields.Char(string="Equipos Asignados")
