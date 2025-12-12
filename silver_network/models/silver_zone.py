# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SilverZone(models.Model):
    _inherit = 'silver.zone'



    node_ids = fields.One2many('silver.node', 'zone_id', string='Nodos')
    node_count = fields.Integer(string='Nodos', compute='_compute_counts')

    #node_count = fields.Integer(string='Conteo de Nodos', compute='_compute_node_count')
    gps_top = fields.Float("GPS Norte", compute='_compute_gps', readonly=True, digits=(10, 7))
    gps_left = fields.Float("GPS Oeste", compute='_compute_gps', readonly=True, digits=(10, 7))
    gps_right = fields.Float("GPS Este", compute='_compute_gps', readonly=True, digits=(10, 7))
    gps_bottom = fields.Float("GPS Sur", compute='_compute_gps', readonly=True, digits=(10, 7))

    @api.depends('node_ids')
    def _compute_counts(self):
        for record in self:
            record.node_count = len(record.node_ids)

    def _compute_gps(self):
        for record in self:
            lats = [asset.silver_address_id.latitude for asset in record.node_ids if asset.silver_address_id.latitude]
            lons = [asset.silver_address_id.longitude for asset in record.node_ids if asset.silver_address_id.longitude]

            if lats:
                record.gps_top = min(lats)
                record.gps_bottom = max(lats)
            else:
                record.gps_top = 0.0
                record.gps_bottom = 0.0

            if lons:
                record.gps_left = min(lons)
                record.gps_right = max(lons)
            else:
                record.gps_left = 0.0
                record.gps_right = 0.0

    def create_core(self):
        self.ensure_one()
        new_node = self.env['silver.node'].create({
            #'name': f"Core for {self.name}",
            'zone_id': self.id,
        })
        return {
            'name': 'Nodo Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.node',
            'view_mode': 'form',
            'res_id': new_node.id,
            'target': 'current',
        }

    def action_create_and_link_node(self):
        self.ensure_one()
        return {
            'name': _('Crear Nodo'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.node',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_zone_id': self.id,
            }
        }

    def action_open_nodes_to_link(self):
        self.ensure_one()
        unassigned_nodes_count = self.env['silver.node'].search_count([('zone_id', '=', False)])
        if unassigned_nodes_count == 0:

            raise UserError(_('No hay Nodes sin asignar.'))

        return {
            'name': 'Agregar Nodo',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.zone.link.node.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
