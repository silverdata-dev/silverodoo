# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SilverAddress(models.Model):
    _inherit = 'silver.address'

    # Añadiendo los campos que apuntan a la localización venezolana
    city_id = fields.Many2one('res.country.city', string='Ciudad')
    municipality_id = fields.Many2one('res.country.municipality', string='Municipio')
    parish_id = fields.Many2one('res.country.parish', string='Parroquia')

    # Re-introduciendo la lógica de onchange con los dominios correctos
    @api.onchange('state_id')
    def _onchange_state_id_l10n_ve(self):
        if self.state_id and self.city_id.state_id != self.state_id:
            self.city_id = False
            self.municipality_id = False
            self.parish_id = False


    @api.onchange('municipality_id')
    def _onchange_municipality_id_l10n_ve(self):
        if self.municipality_id and self.parish_id.municipality_id != self.municipality_id:
            self.parish_id = False
            
    @api.depends('street', 'building', 'house_number', 'zone_id.name', 'parish_id.name')
    def _compute_display_address(self):

        # Sobreescribimos el cómputo para incluir la parroquia
        for rec in self:
            print(("compute", rec))
            parts = [rec.street, rec.building, rec.house_number, rec.zone_id.name, rec.parish_id.name]
            rec.name = ", ".join(filter(None, parts))

