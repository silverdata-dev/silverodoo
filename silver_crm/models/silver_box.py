# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SilverBox(models.Model):
    _inherit = 'silver.box'

    @api.model
    def action_select_nap_and_assign_to_lead(self, box_id, lead_id):
        """
        Este método es llamado por RPC desde el mapa de selección.
        Asigna la caja NAP seleccionada a la oportunidad.
        """
        if not box_id or not lead_id:
            return False

        lead = self.env['crm.lead'].browse(int(lead_id))
        box = self.browse(int(box_id))

        if lead.exists() and box.exists():
            lead.write({'box_id': box.id})
            return True
        return False
