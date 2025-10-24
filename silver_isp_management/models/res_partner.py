# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    contract_ids = fields.One2many('silver.contract', 'partner_id', string='Contratos ISP')
    contract_count = fields.Integer(compute='_compute_contract_count', string='Número de Contratos')

    def _compute_contract_count(self):
        for partner in self:
            partner.contract_count = len(partner.contract_ids)
