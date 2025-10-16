# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campos de l10n_ve_invoice
    nro_ctrl = fields.Char(
        string='Nro. Control',
        size=32,
        copy=False
    )
    invoice_printer = fields.Char(
        string='Factura Impresora Fiscal',
        size=32,
        copy=False
    )
    l10n_ve_document_type = fields.Selection(
        selection=[
            ('out_invoice', 'Factura de Venta'),
            ('out_refund', 'Nota de Crédito de Venta'),
            ('in_invoice', 'Factura de Compra'),
            ('in_refund', 'Nota de Crédito de Compra'),
        ],
        string="Tipo de Documento Fiscal",
        copy=False
    )

    # Campos de l10n_ve_igtf
    l10n_ve_igtf_amount = fields.Monetary(
        string='Monto IGTF',
        copy=False
    )
    l10n_ve_igtf_account_id = fields.Many2one(
        'account.account',
        string='Cuenta de IGTF',
        copy=False
    )
    l10n_ve_igtf_journal_id = fields.Many2one(
        'account.journal',
        string='Diario de IGTF',
        copy=False
    )
