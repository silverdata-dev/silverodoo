# -*- coding: utf-8 -*-

from odoo import models, fields

class ContractContract(models.Model):
    _inherit = 'silver.contract'

    ticket_ids = fields.One2many('silver.ticket', 'contract_id', string='Tickets')
