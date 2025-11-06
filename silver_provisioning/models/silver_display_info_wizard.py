# -*- coding: utf-8 -*-

from odoo import models, fields

class SilverDisplayInfoWizard(models.TransientModel):
    _name = 'silver.display.info.wizard'
    _description = 'Asistente para Mostrar Información de Dispositivo'

    info = fields.Html(string="Información", readonly=True)
