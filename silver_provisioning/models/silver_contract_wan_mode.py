# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverContractWanMode(models.Model):
    _name = 'silver.contract.wan.mode'
    _description = 'Línea de Configuración WAN de Contrato'

    contract_id = fields.Many2one('silver.contract', string='Contrato', required=True, ondelete='cascade')
    name = fields.Char(string='Descripción', default='Configuración WAN')
    vlan_id = fields.Many2one('silver.vlan', string='VLAN ID', related='contract_id.vlan_id')
    protocol = fields.Selection([('pppoe', 'PPPoE'), ('dhcp', 'DHCP'), ('static', 'IP Estática')], string='Protocolo')
