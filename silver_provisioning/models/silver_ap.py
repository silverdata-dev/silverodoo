# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SilverAp(models.Model):
    _inherit = 'silver.ap'
    _inherits = {'silver.access_point': 'access_point_id'}

    access_point_id = fields.Many2one(
        'silver.access_point', 
        string='Registro de Provisioning', 
        required=True, 
        ondelete='cascade',
        help="Registro de provisioning asociado a este AP."
    )


    def action_view_contracts(self):
        return self.access_point_id.action_view_contracts()

    def action_create_contract(self):
        self.ensure_one()
        return {
            'name': _('Create New Contract'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.contract',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_ap_id': self.id,
            }
        }
