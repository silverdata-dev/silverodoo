# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_open_partner(self):
        for p in self:
          #  self.ensure_one()
            print(("openpart", p.partner_id))
            if p.partner_id:
                return {
                    'name': 'Partner',
                    'type': 'ir.actions.act_window',
                    'res_model': 'res.partner',
                    'view_mode': 'form',
                    'res_id': p.partner_id.id,
                    'target': 'new',
                }
        return False
