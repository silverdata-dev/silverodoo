# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverWifiChannelLine(models.Model):
    _name = 'silver.wifi.channel.line'
    _description = 'Canal WiFi Disponible'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    channel_number = fields.Integer(string='Número de Canal')
    frequency_band = fields.Selection([('2.4ghz', '2.4 GHz'), ('5ghz', '5 GHz')], string='Banda de Frecuencia')
