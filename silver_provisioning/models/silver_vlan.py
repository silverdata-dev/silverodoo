# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverVlan(models.Model):
    _inherit = 'silver.vlan'
    contract_id = fields.One2many('silver.contract', 'vlan_id', string="OLT")
    olt_id = fields.One2many('silver.olt', 'vlan_id', string="Contrato")