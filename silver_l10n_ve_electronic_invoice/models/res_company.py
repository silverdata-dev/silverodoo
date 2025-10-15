# -*- coding: utf-8 -*-
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_ve_einvoice_api_url = fields.Char(
        string="URL del API de Facturación Electrónica"
    )
    l10n_ve_einvoice_api_token = fields.Char(
        string="Token del API de Facturación Electrónica",
        password=True
    )
