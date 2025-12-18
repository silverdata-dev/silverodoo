# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverOltCardPort(models.Model):
    _inherit = 'silver.olt.card.port'
    _inherits = {'silver.access_point': 'access_point_id'}

    access_point_id = fields.Many2one(
        'silver.access_point', 
        string='Registro de Provisioning', 
        required=True, 
        ondelete='cascade',
        help="Registro de provisioning asociado a este Puerto OLT."
    )


    def action_create_contract(self):
        self.ensure_one()
        return {
            'name': _('Crear Contrato'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.contract',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_olt_card_port_id': self.id,
            }
        }

    def action_view_contracts(self):
        return self.access_point_id.action_view_contracts()