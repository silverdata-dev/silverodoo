# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    is_change_address_ct = fields.Boolean(string="Cambio Dirección CT")
    
    # Contract Address Data (Readonly/Current)
    # Assumes silver.contract has these fields via l10n_ve extensions, or we use related
    # Since I don't see them in silver_contract, I will define them as Char or related if possible
    
    street_contract = fields.Char(related='contract_id.silver_address_id.street', string="Calle Contrato")
    street2_contract = fields.Char(related='contract_id.silver_address_id.building', string="Edificio Contrato")
    country_contract = fields.Many2one(related='contract_id.silver_address_id.country_id', string="País Contrato")
    state_id_contract = fields.Many2one(related='contract_id.silver_address_id.state_id', string="Estado Contrato")
    city_contract = fields.Char(related='contract_id.silver_address_id.zone_id.name', string="Ciudad/Zona Contrato") # Approximation
    zip_contract = fields.Char(string="ZIP Contrato")
    
    # New Address Data for Contract Change
    address_contract_new = fields.Char(string="Dirección Nueva (Contrato)")
    phone_contract_new = fields.Char(string="Teléfono Nuevo")
    street2_contract_new = fields.Char(string="Edificio Nuevo")
    city_contract_new = fields.Char(string="Ciudad Nueva")
    
    # Extra Fields
    extra_ref_contract = fields.Boolean(string="Referencia Extra")
    floor_level_ct = fields.Selection([('pb', 'PB'), ('1', '1'), ('2', '2')], string="Piso") # Example selection
    building_material_type_ct = fields.Selection([('concrete', 'Concreto'), ('wood', 'Madera')], string="Material")
    ownership_type_ct = fields.Selection([('owned', 'Propio'), ('rented', 'Alquilado')], string="Tenencia")
    
    ote_id_contract = fields.Many2one('silver.zone', string="Sector") # Assuming OTE maps to Zone
    zip_zone = fields.Char(string="ZIP Zona")
    
    contract_latitude_zone = fields.Float(string="Latitud Zona", digits=(10, 7))
    contract_longitude_zone = fields.Float(string="Longitud Zona", digits=(10, 7))

    def action_change_direction_ct(self):
        pass
    
    def geo_localize_change(self):
        pass
