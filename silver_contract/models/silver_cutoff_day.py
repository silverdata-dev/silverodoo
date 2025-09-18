# -*- coding: utf-8 -*-



from odoo import models, fields, api, _


class SilverCutoffDay(models.Model):
    _name = 'silver.cutoff.day'
    _description = 'Día de Corte para Facturación ISP'
    _order = 'day'

    name = fields.Char(string='Nombre', compute='_compute_name', store=True)
    day = fields.Integer(string='Día del Mes', required=True)

    @api.depends('day')
    def _compute_name(self):
        for record in self:
            record.name = f'Día {record.day} de cada mes'
