# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SilverOnuProfile(models.Model):
    _name = 'silver.onu.profile'
    _description = 'Silver ONU Profile'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    tcont_num = fields.Integer(string='Tcont Number', default=1)
    gemport_num = fields.Integer(string='Gemport Number', default=1)
    port_num_eth = fields.Integer(string='Ethernet Port Number', default=4)
    pots = fields.Integer(string='POTS Number', default=1)
    iphost = fields.Integer(string='IP Host Number', default=1)
    ipv6host = fields.Integer(string='IPv6 Host Number', default=1)
    veip = fields.Integer(string='VEIP Number', default=1)
    service_ability_n_1 = fields.Boolean(string='Service Ability N:1')
    service_ability_1_p = fields.Boolean(string='Service Ability 1:P')
    service_ability_1_m = fields.Boolean(string='Service Ability 1:M')
    hardware_model_ids = fields.One2many('silver.hardware.model', 'onu_profile_id', string='Hardware Models')
    firmware_version = fields.Char(string='Firmware Version')
    provisioning_status = fields.Selection([
        ('provisioned', 'Provisioned'),
        ('unprovisioned', 'Unprovisioned'),
        ('error', 'Error'),
    ], string='Status', default='unprovisioned')


    olt_ids = fields.Many2many('silver.olt', 'silver_olt_profile', 'profile_id', 'olt_id', string='OLTs')
