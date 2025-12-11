# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SilverLinkType(models.Model):
    _name = 'silver.linktype'
    _description = 'Silver Link Type'

    code = fields.Char(string='Code', required=True)
    description = fields.Char(string='Description', required=True)
    has_olt = fields.Boolean('Usa OLT', default=False)
    name = fields.Char(string="Nombre")
    service_type_id = fields.Many2one('silver.service.type', string="Tipo de Servicio", required=True, default=lambda self: self._get_default_service_type_id())

    def _get_default_service_type_id(self):
        return self.env['silver.service.type'].search([('code', '=', 'internet')], limit=1)
