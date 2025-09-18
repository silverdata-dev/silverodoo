# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SilverContractRadiusEntry(models.Model):
    _name = 'silver.contract.radius.entry'
    _description = 'Entrada de Log de RADIUS'
    _order = 'session_start desc'

    contract_id = fields.Many2one('silver.contract', string='Contrato', required=True, ondelete='cascade')
    session_start = fields.Datetime(string='Inicio de Sesión')
    session_end = fields.Datetime(string='Fin de Sesión')
    session_duration = fields.Float(string='Duración (horas)', compute='_compute_session_duration', store=True)
    nas_ip_address = fields.Char(string='IP del NAS')
    framed_ip_address = fields.Char(string='IP Asignada al Usuario')

    @api.depends('session_start', 'session_end')
    def _compute_session_duration(self):
        for record in self:
            if record.session_start and record.session_end:
                duration = record.session_end - record.session_start
                record.session_duration = duration.total_seconds() / 3600
            else:
                record.session_duration = 0.0
