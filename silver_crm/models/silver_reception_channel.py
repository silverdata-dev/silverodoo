# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverReceptionChannel(models.Model):
    _inherit = 'silver.reception.channel'
    team_id = fields.Many2one('crm.team', string='Equipo de Ventas Asociado')
