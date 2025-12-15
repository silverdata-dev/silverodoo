# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverNode(models.Model):
    _inherit = 'silver.node'
    _inherits = {'silver.access_point': 'access_point_id'}

    access_point_id = fields.Many2one(
        'silver.access_point',
        string='Registro de Provisioning',
        required=True,
        ondelete='cascade',
        help="Registro de provisioning asociado a este Nodo."
    )


    contract_ids = fields.One2many('silver.contract', 'node_id', string='Contratos')
    contract_count = fields.Integer(related='access_point_id.contract_count', string='Contratos', readonly=True, store=False)



    def action_view_contracts(self):
        return self.access_point_id.action_view_contracts()


    def action_create_contract(self):
        self.ensure_one()
        return {
            'name': _('Crear Contrato'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.contract',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_node_id': self.id,
            }
        }