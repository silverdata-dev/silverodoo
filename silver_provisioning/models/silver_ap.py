# -*- coding: utf-8 -*-
from odoo import models, fields

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
