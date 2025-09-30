# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_open_partner(self):
        self.ensure_one()
        print(("openpart", self.partner_id))
        if self.partner_id:
            return {
                'name': 'Partner',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'res_id': self.partner_id.id,
                'target': 'new',
            }
        return False
