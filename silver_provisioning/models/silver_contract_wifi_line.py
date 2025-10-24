# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverContractWifiLine(models.Model):
    _name = 'silver.contract.wifi.line'
    _description = 'Línea de Configuración WiFi por Contrato'

    contract_id = fields.Many2one('silver.contract', string="Contrato", required=True, ondelete='cascade')
    ssid_index = fields.Integer(string="Índice SSID", required=True, help="Índice numérico de la red WiFi en la ONU (ej: 1 para 2.4GHz, 5 para 5GHz).")
    name = fields.Char(string="Nombre de Red (SSID)", required=True)
    password = fields.Char(string="Contraseña", required=True)
    is_hidden = fields.Boolean(string="Oculta", default=False)
    auth_mode = fields.Selection([
        ('wpapsk/wpa2psk', 'WPA/WPA2-PSK'),
        ('wpa2psk', 'WPA2-PSK'),
        ('open', 'Abierta'),
    ], string="Modo de Autenticación", default='wpapsk/wpa2psk', required=True)
    encrypt_type = fields.Selection([
        ('tkipaes', 'TKIP+AES'),
        ('aes', 'AES'),
    ], string="Tipo de Cifrado", default='tkipaes', required=True)
