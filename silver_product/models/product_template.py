# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pricelist_item_count = fields.Integer(compute='_compute_pricelist_item_count')

    def _compute_pricelist_item_count(self):
        for product in self:
            product.pricelist_item_count = self.env['product.pricelist.item'].search_count([('product_tmpl_id', '=', product.id)])

    # General
    recurring_invoices_ok = fields.Boolean(string="Para facturación recurrente?")
    product_brand_id = fields.Many2one('product.brand', string='Marca')
    model = fields.Char(string='Modelo')


    is_required_brand = fields.Boolean(string="Es numero serie unico?")
    number_list_partner = fields.Char(string="Nombre Plan Padre")
    allow_negative_stock = fields.Boolean(string="Permitir Stock Negativo")
    is_commission_product = fields.Boolean(string="Producto Comisiona")
    commission_percentage = fields.Float(string="Porcentaje de comisión")

    # ISP Data
    is_internet = fields.Boolean(string="Internet")
    uploaded_bandwidth = fields.Float(string="V. de Subida")
    download_bandwidth = fields.Float(string="V. de Descarga")
    is_speed_control = fields.Boolean(string="Control de velocidad")
    sharing_bandwidth_a = fields.Integer(string="a")
    sharing_bandwidth_b = fields.Integer(string="b")
    configure_queue_burst = fields.Boolean(string="Configurar rafaga de cola")
    product_upload_download = fields.Char(string="Producto subida bajada")
    burst_limit_upload = fields.Char(string="Burst Limit Upload")
    burst_limit_download = fields.Char(string="Burst Limit Download")
    burst_threshold_upload = fields.Char(string="Burst Threshold Upload")
    burst_threshold_download = fields.Char(string="Burst Threshold Download")
    burst_time_upload = fields.Char(string="Burst Time Upload")
    burst_time_download = fields.Char(string="Burst Time Download")
    queue_priority_upload = fields.Char(string="Prioridad Subida")
    queue_priority_download = fields.Char(string="Prioridad Bajada")
    is_custom_traffic_table = fields.Boolean(string="Custom Traffic Table")
    name_custom_traffic_table = fields.Char(string="Name Custom Traffic Table")
    is_custom_address_list = fields.Boolean(string="Custom AddresList")
    name_address_list = fields.Char(string="Name Custom AddresList")
    is_product_vlan = fields.Boolean(string="Vlans-Profiles por Producto")
    s_vlan = fields.Char(string="s-vlan-profile")
    c_vlan = fields.Char(string="c-vlan-profile")
    name_custom_profile = fields.Char(string="Name Custom Profile")
    traffic_profile_index = fields.Char(string="Index Traffic Profile")
    radius_id = fields.Many2one('res.partner', string="Radius") # Assuming a model, using res.partner as placeholder
    radius_attributes_ids = fields.Many2many('res.partner', string="Radius Attributes") # Placeholder
    profile_radius = fields.Char(string="Profile Radius")
    is_custom_tcon_profile = fields.Boolean(string="Custom TCON")
    name_custom_tcon_profile = fields.Char(string="Name Custom TCON")
    is_custom_pppoe_profile = fields.Boolean(string="Custom PPPoE Profile")
    name_custom_pppoe_profile = fields.Char(string="Name Custom PPPoE Profile")
    qty_extra_stock = fields.Float(string="Cantidad Cubierta")
    
    # IP Addressing
    #type_access_net = fields.Selection([('dhcp_leases', 'DHCP Leases')], string="Network Access Type")
    #dhcp_custom_server = fields.Char(string="DHCP Leases")
    #interface = fields.Char(string="Interface")
    #is_multiple_vlans = fields.Boolean(string="Habilitar multiples Vlans")
    #ip_address_line_ids = fields.One2many('product.ip.address.line', 'product_tmpl_id', string="IP Address Lines")
    #ip_address_ids = fields.One2many('product.ip.address', 'product_tmpl_id', string="IP Addresses")

    # IPTV Data
    is_iptv = fields.Boolean(string="IPTV")
    code_ott = fields.Char(string="Codigo OTT")


    def action_open_label_layout(self):
        pass

    def action_update_quantity_on_hand(self):
        pass

    def open_pricelist_rules(self):
        pass

    def action_open_quants(self):
        pass

    def action_product_tmpl_forecast_report(self):
        pass

    def action_view_stock_move_lines(self):
        pass

    def action_view_orderpoints(self):
        pass

    def action_open_product_lot(self):
        pass

    def action_view_related_putaway_rules(self):
        pass

    def action_view_po(self):
        pass

    def action_view_sales(self):
        pass

    def action_variantes(self):
        pass

    def action_create_group(self):
        pass

# Dummy models for One2many relationships, you might need to create these properly
class ProductIpAddressLine(models.Model):
    _name = 'product.ip.address.line'
    _description = 'Product IP Address Line'
    product_tmpl_id = fields.Many2one('product.template')
    name = fields.Char("Name")

class ProductIpAddress(models.Model):
    _name = 'product.ip.address'
    _description = 'Product IP Address'
    product_tmpl_id = fields.Many2one('product.template')
    name = fields.Char("Name")

