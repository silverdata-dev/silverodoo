# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SilverBox(models.Model):
    _inherit = 'silver.box'
    _inherits = {'silver.access_point': 'access_point_id'}

    access_point_id = fields.Many2one(
        'silver.access_point', 
        string='Registro de Provisioning', 
        required=True, 
        ondelete='cascade',
        help="Registro de provisioning asociado a esta Caja."
    )

    contract_ids = fields.One2many('silver.contract', 'box_id', string='Contratos')
    capacity_usage_nap = fields.Integer(string='Usada NAP', compute='_compute_capacity_usage_nap', store=True)

    @api.depends('contract_ids')
    def _compute_capacity_usage_nap(self):
        for box in self:
            box.capacity_usage_nap = len(box.contract_ids)

    def action_view_contracts(self):
        return self.access_point_id.action_view_contracts()
