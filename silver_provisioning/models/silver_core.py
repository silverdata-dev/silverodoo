# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverCore(models.Model):
    _inherit = 'silver.core'
    _inherits = {'silver.access_point': 'access_point_id'}

    access_point_id = fields.Many2one(
        'silver.access_point', 
        string='Registro de Provisioning', 
        required=True, 
        ondelete='cascade',
        help="Registro de provisioning asociado a este Core."
    )


    contract_ids = fields.One2many('silver.contract', 'core_id', string='Contratos')
    contract_count = fields.Integer(related='access_point_id.contract_count', string='Contratos', readonly=True, store=True)



    def action_view_contracts(self):
        return self.access_point_id.action_view_contracts()