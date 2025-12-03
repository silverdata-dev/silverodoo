# -*- coding: utf-8 -*-

from odoo import models, fields

class ContractContract(models.Model):
    _inherit = 'silver.contract'

    ticket_ids = fields.One2many('helpdesk.ticket', 'contract_id', string='Tickets')
