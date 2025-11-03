# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SilverContractSelectOnuWizard(models.TransientModel):
    _name = 'silver.contract.select.onu.wizard'
    _description = 'Asistente para Seleccionar ONU Descubierta'

    contract_id = fields.Many2one(
        'silver.contract',
        string='Contrato',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('active_id')
    )
    discovered_onu_id = fields.Many2one(
        'silver.olt.discovered.onu',
        string='ONU Descubierta',
        required=True,
        domain="[('olt_id', '=', parent.olt_id), ('is_assigned', '=', False)]"
    )
    olt_id = fields.Many2one(related='contract_id.olt_id')

    def action_apply_onu(self):
        """
        Aplica los datos de la ONU seleccionada al contrato llamando al método
        centralizado y luego marca la ONU como 'asignada'.
        """
        self.ensure_one()
        if not self.contract_id or not self.discovered_onu_id:
            raise UserError(_("Se requiere un contrato y una ONU para continuar."))

        # --- 1. Obtener los valores del método centralizado ---
        vals_to_write = self.contract_id._prepare_contract_values_from_onu(self.discovered_onu_id)

        # --- 2. Asignar los datos al Contrato ---
        if vals_to_write:
            self.contract_id.write(vals_to_write)

        # --- 3. Marcar la ONU descubierta como asignada ---
        self.discovered_onu_id.write({
            'is_assigned': True,
            'contract_id': self.contract_id.id
        })

        return {'type': 'ir.actions.act_window_close'}
