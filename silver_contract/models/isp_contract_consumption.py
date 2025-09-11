# -*- coding: utf-8 -*-
from odoo import models, fields, api

class IspContractConsumption(models.Model):
    _name = 'isp.contract.consumption'
    _description = 'Registro de Consumo de Datos del Contrato'
    _order = 'date desc'

    contract_id = fields.Many2one('isp.contract', string='Contrato', required=True, ondelete='cascade')
    date = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now, required=True)
    upload_gb = fields.Float(string='Subida (GB)')
    download_gb = fields.Float(string='Bajada (GB)')
    total_gb = fields.Float(string='Total (GB)', compute='_compute_total_gb', store=True)

    @api.depends('upload_gb', 'download_gb')
    def _compute_total_gb(self):
        for record in self:
            record.total_gb = record.upload_gb + record.download_gb
