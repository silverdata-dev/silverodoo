# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import ipaddress


class SilverIpAddress(models.Model):
    _inherit = 'silver.ip.address'

    contract_ids = fields.One2many('silver.contract', 'ip_address_id', string="Contratos")
    contract_id = fields.Many2one("silver.contract", string="Contrato", compute='_compute_contract_id',
        inverse='_inverse_contract_id',
        store=True
    )

    def action_view_contract(self):
        """
        Opens the form view of the associated contract.
        """
        self.ensure_one()
        if self.contract_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'silver.contract',
                'view_mode': 'form',
                'res_id': self.contract_id.id,
                'target': 'current',
            }
        return {'type': 'ir.actions.act_window_close'}

    @api.depends('contract_ids')
    def _compute_contract_id(self):
        """Calcula el Many2one tomando el primer (y único) registro del One2many."""
        for node in self:
            # Como es un One2One simulado, solo tomamos el primer registro si existe.
            node.contract_id = node.contract_ids[:1] or False

    def _inverse_contract_id(self):
        """Maneja la escritura del campo. Es la CLAVE para atar."""
        for node in self:
            if node.contract_id:
                # Caso A: El usuario selecciona un contract_id existente.
                # Lo vincula al node actual y desvincula los contract_ids anteriores (si los hay).
                node.contract_ids = [(6, 0, [node.contract_id.id])]
            else:
                # Caso B: El usuario borra la selección.
                # Desvincula todos los contract_ids asociados.
                node.contract_ids = [(5, 0, 0)]