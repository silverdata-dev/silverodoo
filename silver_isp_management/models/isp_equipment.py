# -*- coding: utf-8 -*-
from odoo import models, fields

class IspEquipment(models.Model):
    _name = 'isp.equipment'
    _description = 'Equipo de Cliente ISP'

    name = fields.Char(string='Nombre del Equipo', compute='_compute_name', store=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    serial_number = fields.Char(string='Número de Serie/MAC', required=True)
    
    contract_id = fields.Many2one('silver.contract', string='Contrato', required=True, ondelete='cascade')
    partner_id = fields.Many2one(related='contract_id.partner_id', string='Cliente', store=True)

    state = fields.Selection([
        ('in_stock', 'En Almacén'),
        ('installed', 'Instalado'),
        ('in_repair', 'En Reparación'),
        ('retired', 'Retirado'),
    ], string='Estado', default='installed')

    _sql_constraints = [
        ('serial_number_uniq', 'unique(serial_number)', '¡El número de serie/MAC ya existe!')
    ]

    def _compute_name(self):
        for record in self:
            record.name = f"{record.product_id.name} ({record.serial_number})"
