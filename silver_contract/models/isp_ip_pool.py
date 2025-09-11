# -*- coding: utf-8 -*-
from odoo import models, fields

class IspIpPool(models.Model):
    _name = 'isp.ip.pool'
    _description = 'Pool de Direcciones IP'

    name = fields.Char(string='Nombre del Pool', required=True)
    network_address = fields.Char(string='Dirección de Red (ej: 192.168.1.0/24)')
    gateway = fields.Char(string='Gateway')
    ip_line_ids = fields.One2many('isp.ip.pool.line', 'pool_id', string='Líneas de IP')

class IspIpPoolLine(models.Model):
    _name = 'isp.ip.pool.line'
    _description = 'Línea de Pool de IP'
    _order = 'ip_address'

    pool_id = fields.Many2one('isp.ip.pool', string='Pool de IP', required=True, ondelete='cascade')
    ip_address = fields.Char(string='Dirección IP', required=True)
    is_assigned = fields.Boolean(string='Asignada', readonly=True)
    assigned_contract_id = fields.Many2one('isp.contract', string='Contrato Asignado', readonly=True)
