# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverPingWizard(models.TransientModel):
    _name = 'silver.ping.wizard'
    _description = 'Asistente para Mostrar Resultado de Ping'

    ping_output = fields.Text(string="Resultado", readonly=True)
