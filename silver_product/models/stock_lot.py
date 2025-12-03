# -*- coding: utf-8 -*-
from odoo import models, fields

class StockLot(models.Model):
    _inherit = 'stock.lot'

    external_equipment = fields.Boolean(string='Equipo externo')
    serial_number = fields.Char(string='Número Serial', related='name')
    applied_accounting_cost = fields.Boolean(string='Costo Contable Aplicado')

    software_version  = fields.Char(string='Versión software')
    firmware_version = fields.Char(string='Firmware Version', readonly=False)

    brand_id = fields.Many2one('product.brand', string="Marca", related='product_id.product_brand_id')
    brand_logo = fields.Binary(related='brand_id.logo', string='Logo de la Marca')
    #brand_name = fields.Char(string='Marca',  store=True)
    #model_name = fields.Char(string='Modelo',  store=True)
    mac_address = fields.Char(string='MAC Address', store=True)
    hardware_model_id = fields.Many2one('silver.hardware.model', string='Modelo',related='product_id.hardware_model_id')
    #onu_profile_id = fields.Many2one('silver.onu.profile', string='ONU Profile')

    etype = fields.Selection([('core', 'Core'), ('olt', 'OLT'), ('onu', 'ONU'), ('ap', 'AP'), ('ecp', 'ECP'), ('splitter', 'Splitter'), ('box', 'NAP'), ], string='Tipo de equipo', related="hardware_model_id.etype")
    manual = fields.Boolean(string='Configuración Manual', related="hardware_model_id.manual")


    product_id = fields.Many2one(
        'product.product', 'Product', index=True,
        domain=("[('tracking', '!=', 'none'), ('type', '=', 'product')] +"
            " ([('product_tmpl_id', '=', context['default_product_tmpl_id'])] if context.get('default_product_tmpl_id') else [])"),
        required=False, check_company=True)

    # Cuando el product_id cambia, actualizamos la marca y el modelo
    # Asumimos que product.product tiene campos 'brand_name' y 'model_name'
    def _onchange_product_id(self):
        if self.product_id:
            self.brand_id = self.product_id.brand_id
            self.hardware_model_id = self.product_id.hardware_model_id
            #self.brand_name = self.product_id.brand_name
            #self.model_name = self.product_id.model_name
        else:
            self.brand_name = False
            self.model_name = False