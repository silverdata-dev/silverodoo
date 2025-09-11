# -*- coding: utf-8 -*-
from odoo import models, fields

class IspContractWanMode(models.Model):
    _name = 'isp.contract.wan.mode'
    _description = 'Línea de Configuración WAN de Contrato'

    contract_id = fields.Many2one('isp.contract', string='Contrato', required=True, ondelete='cascade')
    name = fields.Char(string='Descripción', default='Configuración WAN')
    vlan_id = fields.Integer(string='VLAN ID')
    protocol = fields.Selection([('pppoe', 'PPPoE'), ('dhcp', 'DHCP'), ('static', 'IP Estática')], string='Protocolo')
