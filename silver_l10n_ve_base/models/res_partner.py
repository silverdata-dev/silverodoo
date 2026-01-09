# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, api, _

import re

# Definición de los patrones
PATRON_VZ = r'^(\+58)?\s?\(?0?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}$'
PATRON_GENERICO = r'^\+\d{1,3}[\s\-\.]?\(?\d{1,4}\)?[\s\-\.]?\d{4,10}$'


def validar_telefono(numero):
    """
    Valida un número de teléfono: estrictamente si es venezolano,
    o de forma genérica si es internacional.

    Retorna True si es válido, False en caso contrario.
    Retorna 'VZ' si es un match venezolano, 'INT' si es genérico.
    """
    if not isinstance(numero, str):
        return False, 'ERROR'

    # Limpiar el número de caracteres no numéricos o '+' para una verificación inicial (opcional)
    # numero_limpio = re.sub(r'[^\d\+]', '', numero)

    # 1. PRUEBA VENEZOLANA (Estricta)
    if re.fullmatch(PATRON_VZ, numero):
        return True, 'VZ'

    # 2. PRUEBA GENÉRICA (Si no es VZ, debe ser internacional)
    # Si la cadena empieza con '+' se asume que intenta ser un formato internacional
    if numero.startswith('+') and re.fullmatch(PATRON_GENERICO, numero):
        return True, 'INT'

    # 3. Si no cumple ninguno de los dos
    return False, 'NONE'

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
    def check_vat(self, validation=None):


        print(("vat test3", self.vat))
        return True

    def _check_vat(self, validation=None):
        return super()._check_vat()

    @api.model
    def _run_vat_test(self, vat_number, default_country, partner_is_company=True):
        print(("vat test2", vat_number))
        return True

    @api.constrains('phone')
    def check_phone(self):

        if not self.phone:
            return True

        v, s = validar_telefono(self.phone)
        if not v:
            raise UserError(_("Número de teléfono no válido"))

        print(("validar", v, s))


        return not v


