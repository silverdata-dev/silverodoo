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
    brand_id = fields.Many2one('product.brand', string='Marca')
    brand_logo = fields.Binary(related='brand_id.logo', string='Logo de la Marca')
    #hardware_model_id = fields.Many2one('silver.hardware.model', string='Modelo')
    etype = fields.Selection(
        [('core', 'Router'), ('olt', 'OLT'), ('onu', 'ONU'), ('ap', 'AP'), ('ecp', 'ECP'), ('splitter', 'Splitter'),
         ('box', 'NAP'), ], string='Tipo de equipo')

    manual = fields.Boolean(string='Configuración Manual')

    onu_profile_id = fields.Many2one('silver.onu.profile', string='ONU Profile')


    service_type_id = fields.Many2one('silver.service.type', string= "Tipo de Servicio", default=lambda self: self._default_service_type())


    is_required_brand = fields.Boolean(string="Es numero serie unico?")
    number_list_partner = fields.Char(string="Nombre Plan Padre")
    allow_negative_stock = fields.Boolean(string="Permitir Stock Negativo")
    is_commission_product = fields.Boolean(string="Producto Comisiona")
    commission_percentage = fields.Float(string="Porcentaje de comisión")

    # ISP Data
    is_internet = fields.Boolean(string="Internet", compute="_compute_is_internet")
    min_upload_bandwidth = fields.Float(string="V. Min. de Subida", default='1')
    min_download_bandwidth = fields.Float(string="V. Min. de Descarga", default='1')
    upload_bandwidth = fields.Float(string="V. de Subida", default='50')
    download_bandwidth = fields.Float(string="V. de Descarga", default='100')
    burst_limit_upload = fields.Float(string="Burst Limit Upload", default='0')
    burst_limit_download = fields.Float(string="Burst Limit Download", default='0')
    burst_threshold_upload = fields.Float(string="Burst Threshold Upload", default='0')
    burst_threshold_download = fields.Float(string="Burst Threshold Download", default='0')
    burst_time_upload = fields.Integer(string="Burst Time Upload", default='0')
    burst_time_download = fields.Integer(string="Burst Time Download", default='0')
    queue_priority = fields.Integer(string="Prioridad", default='8')

    #tracking = fields.Selection(related='product_id.tracking'
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



    @api.model
    def default_get(self, fields):
        # 1. Obtener los valores por defecto actuales
        res = super(ProductTemplate, self).default_get(fields)

        # 2. Reemplazar el valor de 'detailed_type' si está en los campos solicitados
        if 'type' in fields:
            # Puedes poner aquí la lógica condicional que necesites
            res['type'] = 'consu' #aaa

        return res

    @api.onchange("type")
    def _onchange_type(self):
        if self.type == 'product' and self.tracking == 'none':
            self.tracking = 'lot'

    def _compute_is_internet(self):
        for a in self:
            a.is_internet = (a.service_type_id and a.service_type_id.code == 'internet')

    def _default_service_type(self):


        return self.env["silver.service.type"].search([('code', '=', 'internet')], limit=1)

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
