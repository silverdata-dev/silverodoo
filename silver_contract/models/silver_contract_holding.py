# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverContractHolding(models.Model):
    _name = 'silver.contract.holding'
    _description = 'Holding o Grupo de Contratos'
    _order = 'name'

    name = fields.Char(string='Nombre del Holding', required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente Principal')
    #contract_ids = fields.One2many('silver.contract', 'holding_id', string='Contratos en este Holding')
    notes = fields.Text(string='Notas')
