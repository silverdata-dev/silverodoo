# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProvisioningWizard(models.TransientModel):
    _name = 'silver.provisioning.wizard'
    _description = 'Asistente para Aprovisionamiento de Servicios OLT'

    contract_id = fields.Many2one('silver.contract', string='Contrato', required=True)
    olt_id = fields.Many2one('silver.olt', string='OLT', related='contract_id.olt_id', readonly=True)
    
    # Campos para Aprovisionar
    pon_port = fields.Char(string='Puerto PON (ej. 0/1)')
    onu_id = fields.Char(string='ID de ONU (ej. 1)')
    serial_number = fields.Char(string='Número de Serie ONU')

    def action_apply_provision(self):
        self.ensure_one()
        # Los datos como pon_port, onu_id y serial_number se obtienen ahora directamente
        # desde el contrato dentro de la función action_provision_onu.
        self.olt_id.action_provision_onu(self.contract_id)
        self.contract_id.write({
            'state_service': 'active',
            'date_active': fields.Date.context_today(self)
        })
        return {'type': 'ir.actions.act_window_close'}

    def action_apply_cutoff(self):
        self.ensure_one()
        self.olt_id.action_disable_onu(self.pon_port, self.onu_id)
        self.contract_id.write({
            'state_service': 'disabled',
            'date_cut': fields.Date.context_today(self)
        })
        return {'type': 'ir.actions.act_window_close'}

    def action_apply_reconnection(self):
        self.ensure_one()
        self.olt_id.action_enable_onu(self.pon_port, self.onu_id)
        self.contract_id.write({
            'state_service': 'active',
            'date_reconnection': fields.Date.context_today(self)
        })
        return {'type': 'ir.actions.act_window_close'}
