# -*- coding: utf-8 -*-
from odoo import models, fields, api



class ResPartner(models.Model):
    _inherit = 'res.partner'

    city_id = fields.Many2one("res.country.city", string="City", related="silver_address_id.city_id")
    municipality_id = fields.Many2one('res.country.municipality', string='Municipio', related="silver_address_id.municipality_id")

    street = fields.Char(string="Call", related="silver_address_id.street")
    municipality = fields.Many2one("res.country.municipality", "Municipality", related="municipality_id")

    # Reemplazando los campos de silver.address con los de la localización
    parish_id = fields.Many2one('res.country.parish', string='Parroquia', related="silver_address_id.parish_id", domain="[('municipality_id', '=', municipality)]")

    # El campo city ya existe en res.partner, así que no es necesario re-declararlo.
    # El campo state_id ya existe en res.partner.
    # El campo country_id ya existe en res.partner.

    # Adaptación de la lógica onchange
    @api.onchange('country_id')
    def _onchange_country_id_l10n_ve(self):
        if self.country_id and self.state_id.country_id != self.country_id:
            self.state_id = False
            self.municipality_id = False
            self.parish_id = False
            self.city_id = False

    @api.onchange('state_id')
    def _onchange_state_id_l10n_ve(self):
        if self.state_id and self.municipality_id.state_id != self.state_id:
            self.municipality_id = False
            self.parish_id = False
            self.city_id = False

    @api.onchange('municipality_id')
    def _onchange_municipality_id_l10n_ve(self):
        if self.municipality_id and self.parish_id.municipality_id != self.municipality_id:
            self.parish_id = False


    @api.model
    def simple_vat_check(self, country_code, vat_number):
        print(("vat test1", vat_number))
        return True

    @api.constrains('vat', 'country_id')
    def check_vat(self):


        print(("vat test3", self.vat))
        return True

    @api.model
    def _run_vat_test(self, vat_number, default_country, partner_is_company=True):
        print(("vat test2", vat_number))
        return True



