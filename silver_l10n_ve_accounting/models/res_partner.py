# -*- coding: utf-8 -*-
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_receivable_id = fields.Many2one(
        'account.account',
        string="Cuenta a Cobrar",
      #  domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('company_id', '=', company_id)]",
        company_dependent=True,
        help="Esta cuenta se utilizará en los asientos de facturas de cliente como la cuenta a cobrar para este contacto."
    )
    property_account_payable_id = fields.Many2one(
        'account.account',
        string="Cuenta a Pagar",
      #  domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False), ('company_id', '=', company_id)]",
        company_dependent=True,
        help="Esta cuenta se utilizará en los asientos de facturas de proveedor como la cuenta a pagar para este contacto."
    )
