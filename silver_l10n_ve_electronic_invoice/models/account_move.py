# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

from .electronic_invoice_provider import ElectronicInvoiceProvider

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    electronic_invoice_state = fields.Selection(
        selection=[
            ('draft', 'No Enviado'),
            ('sent', 'Enviado'),
            ('accepted', 'Aceptado'),
            ('rejected', 'Rechazado'),
        ],
        string="Estado Factura Electrónica",
        default='draft',
        copy=False,
        tracking=True
    )
    electronic_invoice_cud = fields.Char(
        string="CUD Electrónico",
        help="Código Único de Documento devuelto por el proveedor.",
        readonly=True,
        copy=False
    )
    electronic_invoice_qr_code = fields.Char(
        string="URL del Código QR",
        readonly=True,
        copy=False
    )
    electronic_invoice_last_error = fields.Text(
        string="Último Error",
        readonly=True,
        copy=False
    )

    def action_send_electronic_invoice(self):
        for move in self:
            if move.state != 'posted':
                raise UserError(_("La factura debe estar validada para poder enviarla electrónicamente."))
            if move.move_type not in ('out_invoice', 'out_refund'):
                raise UserError(_("Este tipo de documento no puede ser enviado electrónicamente."))

            # Instanciar y usar el conector
            provider = ElectronicInvoiceProvider(move.company_id)
            try:
                response = provider.send_invoice(move)
                if response.get('success'):
                    move.write({
                        'electronic_invoice_state': 'accepted',
                        'electronic_invoice_cud': response.get('cud'),
                        'electronic_invoice_qr_code': response.get('qr_code_url'),
                        'electronic_invoice_last_error': False,
                    })
                    move.message_post(body=_("Factura electrónica enviada y aceptada con CUD: %s") % response.get('cud'))
                else:
                    error_message = response.get('error', 'Error desconocido del proveedor.')
                    move.write({
                        'electronic_invoice_state': 'rejected',
                        'electronic_invoice_last_error': error_message,
                    })
                    move.message_post(body=_("Error al enviar factura electrónica: %s") % error_message)

            except Exception as e:
                _logger.error("Fallo al llamar al API de facturación electrónica: %s", str(e))
                move.write({
                    'electronic_invoice_state': 'rejected',
                    'electronic_invoice_last_error': str(e),
                })
                move.message_post(body=_("Fallo de conexión con el API: %s") % str(e))

        return True
