# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import librouteros


class SilverVlan(models.Model):
    _name = 'silver.vlan'
    _description = 'Placeholder for Silver VLAN'
    name = fields.Char('Descripción')
    vlanid = fields.Integer('Vlan ID')
    #olt_ids = fields.One2many('silver.olt', 'vlan_id', string='OLTs')
    node_id = fields.Many2one('silver.node',  string='Node')
    olt_ids = fields.Many2many('silver.olt', 'silver_mvlan_olt',  'vlan_id', 'olt_id',  string='OLT')
    olt_port_ids = fields.Many2many('silver.olt.card.port', 'silver_mvlan_olt_port',  'vlan_id', 'olt_port_id', string='PON')
    core_ids = fields.Many2many('silver.core', 'silver_mvlan_core',  'vlan_id', 'core_id',   string='Core')

    vtype = fields.Selection([('s-vlan', 'S-vlan'), ('c-vlan', 'C-vlan'), ('management', 'Administración')], string="Tipo")

    @api.onchange('vlanid')
    def _onchange_vlanid(self):
        for s in self:
            if (not s.name) or (s.name.isdigit()):
                s.name = f"{ s.vlanid}"

