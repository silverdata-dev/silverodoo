# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverReceptionChannel(models.Model):
    _name = 'silver.reception.channel'
    _description = 'Canal de Recepción de Clientes'
    _order = 'name'

    name = fields.Char(string='Nombre del Canal', required=True)
    is_internal_referral = fields.Boolean(string='Es Referido Interno')
    commission_percentage = fields.Float(string='Porcentaje de Comisión')
    team_id = fields.Many2one('crm.team', string='Equipo de Ventas Asociado')
