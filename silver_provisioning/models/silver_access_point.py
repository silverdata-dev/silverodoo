# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SilverAccessPoint(models.Model):
    _name = 'silver.access_point'
    _description = 'Punto de Acceso Silver (Provisioning)'

    name = fields.Char(string="Nombre", required=True, index=True, default='Nuevo')
    contract_ids = fields.One2many('silver.contract', 'access_point_id', string='Contratos')

    contract_count = fields.Integer(string="Contratos", compute='_compute_contract_count')



    def _compute_contract_count(self):
        for record in self:
            # Assuming 'silver.contract' has a 'ap_id' field.
            record.contract_count = self.env['silver.contract'].search_count([('ap_id', '=', record.id)])


    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': 'Contratos',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.contract',
            'view_mode': 'tree,form',
            'domain': [('ap_id', '=', self.id)],
            'context': {'default_ap_id': self.id},
            'target': 'current',
        }
