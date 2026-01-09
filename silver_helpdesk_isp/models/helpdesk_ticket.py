# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # --- ISP / Network Technical Fields ---

    # Current/New Technical Data
    node_id = fields.Many2one('silver.node', string="Nodo")
    box_id = fields.Many2one('silver.box', string="Caja NAP")
    #port_nap_id = fields.Many2one('silver.nap.port', string="Puerto NAP") # Verify model name
    #port_nap = fields.Many2one('silver.nap.port', string="Puerto NAP (Alt)") # In snippet
    ap_id = fields.Many2one('silver.ap', string="AP")
    core_id = fields.Many2one('silver.core', string="Equipo Router")
    
    olt_id = fields.Many2one('silver.olt', string="Equipo OLT")
    olt_card_id = fields.Many2one('silver.olt.card', string="Tarjeta OLT")
    olt_port_id = fields.Many2one('silver.olt.card.port', string="Puerto OLT") # Verify model
    splitter_id = fields.Many2one('silver.splitter', string="Splitter")
    
    service_port = fields.Integer(string="Service Port")
    onuid = fields.Integer(string="ONU-ID")
    ip_address = fields.Char(string="Dirección IP")
    
    # Management IP
    service_port_mgn = fields.Integer(string="Service Port MGN")
    ip_address_mgn = fields.Char(string="IP MGN")

    # Old Technical Data (For Change Address/Equipment processes)
    address_old = fields.Char(string="Dirección Anterior")
    street_old = fields.Char(string="Calle Anterior")
    secundary_street_old = fields.Char(string="Calle Secundaria Anterior")
    address_ref_old = fields.Char(string="Referencia Anterior")
    
    node_id_old = fields.Many2one('silver.node', string="Nodo Anterior")
    box_id_old = fields.Many2one('silver.box', string="Caja NAP Anterior")
    #port_nap_old = fields.Many2one('silver.nap.port', string="Puerto NAP Anterior")
    ap_id_old = fields.Many2one('silver.ap', string="AP Anterior")
    core_id_old = fields.Many2one('silver.core', string="Equipo Router Anterior")
    
    olt_id_old = fields.Many2one('silver.olt', string="Equipo OLT Anterior")
    olt_card_id_old = fields.Many2one('silver.olt.card', string="Tarjeta OLT Anterior")
    olt_port_id_old = fields.Many2one('silver.olt.card.port', string="Puerto OLT Anterior")
    
    service_port_old = fields.Integer(string="Service Port Anterior")
    onuid_old = fields.Integer(string="ONU-ID Anterior")
    ip_address_old = fields.Char(string="Dirección IP Anterior")
    
    service_port_mgn_old = fields.Integer(string="Service Port MGN Anterior")
    ip_address_mgn_old = fields.Char(string="IP MGN Anterior")

    # New Location Data (If different from address_contract)
    address = fields.Char(string="Dirección Nueva")
    country_id = fields.Many2one('res.country', string="País")
    state_id = fields.Many2one('res.country.state', string="Estado")
    street = fields.Char(string="Calle Nueva")
    secundary_street_new = fields.Char(string="Calle Secundaria Nueva")
    address_ref_new = fields.Char(string="Referencia Nueva")
    zip = fields.Char(string="ZIP")
    
    contract_latitude = fields.Float(string="Latitud", digits=(10, 7))
    contract_longitude = fields.Float(string="Longitud", digits=(10, 7))
    date_localization = fields.Datetime(string="Fecha Localización")

    # Flags
    is_change_address = fields.Boolean(string="Cambio de Domicilio")
    
    # Flags for Equipment Change
    is_device_external = fields.Boolean(string="Equipo Externo")
    is_change_new_bridge = fields.Boolean()
    is_change_onu = fields.Boolean(string="Cambio ONU")
    serial_onu_back = fields.Char(string="Serial ONU Retira")
    external_serial_onu_old = fields.Char()
    model_onu_type_old_id = fields.Many2one('product.product', string="Modelo ONU Ant.")
    
    new_mac = fields.Char(string="Nueva MAC")
    serial_onu_new = fields.Char(string="Serial ONU Nuevo")
    product_serial_id = fields.Many2one('stock.lot', string="Serial Producto")
    model_onu_type_id = fields.Many2one('product.product', string="Modelo ONU Nuevo")
    external_serial_onu_new = fields.Char()
    external_model_onu_type_id = fields.Many2one('product.product')
    is_device_external_ticket = fields.Boolean()
    
    is_change_bridge = fields.Boolean()
    is_device_extra = fields.Boolean()
    is_add_ip_contract = fields.Boolean()
    is_mgn_service_port = fields.Boolean()
    is_change_device = fields.Boolean()
    is_change_mac = fields.Boolean()
    is_change_antena_mac = fields.Boolean()
    
    # WiFi
    is_change_antena = fields.Boolean()
    serial_antena_back = fields.Char()
    model_antena_back = fields.Char()
    external_serial_antena_back = fields.Char()
    external_model_antena_back = fields.Char()
    
    serial_antena_new = fields.Char()
    model_antena_new = fields.Char()
    external_serial_antena_new = fields.Char()
    external_model_antena_new = fields.Char()
    new_antena_mac = fields.Char()
    
    is_change_router = fields.Boolean()
    serial_router_back = fields.Char()
    model_router_back = fields.Char()
    serial_router_new = fields.Char()
    model_router_new = fields.Char()
    is_equipment_external_wifi = fields.Boolean()

    # Dynamic Pool
    is_used_dynamic_pool = fields.Boolean()
    new_pool_ip_contract = fields.Char()

    # Integration
    is_password_odoo = fields.Boolean()

    linktype_id = fields.Many2one('silver.linktype', string="Tipo de Conexión",
                                related="contract_id.linktype_id")


    def action_change_device(self):
        pass

