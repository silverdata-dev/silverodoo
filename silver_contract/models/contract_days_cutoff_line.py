# -*- coding: utf-8 -*-
from odoo import models, fields

class ContractDaysCutoffLine(models.Model):
    _name = 'contract.days.cutoff.line'
    _description = 'Línea de Días de Corte del Contrato'

    cutoff_date_id = fields.Many2one('silver.cutoff.date', string='Periodo de Consumo')
    day_from = fields.Integer(string='Desde el día')
    day_to = fields.Integer(string='Hasta el día')
    days_grace = fields.Integer(string='Días de Gracia Adicionales')
