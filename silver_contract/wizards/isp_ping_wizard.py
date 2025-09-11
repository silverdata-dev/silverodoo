# -*- coding: utf-8 -*-
from odoo import models, fields

class IspPingWizard(models.TransientModel):
    _name = 'isp.ping.wizard'
    _description = 'Asistente para Mostrar Resultado de Ping'

    ping_output = fields.Text(string="Resultado", readonly=True)
