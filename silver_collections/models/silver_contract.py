# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

from .agnostic_payment_connector import AgnosticPaymentConnector

_logger = logging.getLogger(__name__)

class SilverContract(models.Model):
    _inherit = 'silver.contract'

    transaction_ids = fields.One2many('payment.transaction', 'contract_id', string="Transacciones de Pago")
    payment_state = fields.Selection(
        selection=[
            ('unpaid', 'No Pagado'),
            ('in_progress', 'Pago en Progreso'),
            ('paid', 'Pagado'),
        ],
        string="Estado de Pago",
        compute='_compute_payment_state',
        store=True
    )

    @api.depends('transaction_ids.state')
    def _compute_payment_state(self):
        for contract in self:
            if any(tx.state == 'done' for tx in contract.transaction_ids):
                contract.payment_state = 'paid'
            elif any(tx.state == 'pending' for tx in contract.transaction_ids):
                contract.payment_state = 'in_progress'
            else:
                contract.payment_state = 'unpaid'

    def action_initiate_payment(self):
        self.ensure_one()
        if self.payment_state == 'paid':
            raise UserError(_("Este contrato ya ha sido pagado."))

        # Encuentra un proveedor de pago activo (en el futuro podrías seleccionarlo)
        provider = self.env['payment.provider'].search([('state', '!=', 'disabled')], limit=1)
        if not provider:
            raise UserError(_("No hay proveedores de pago activos configurados."))

        # Crea el registro de la transacción
        transaction = self.env['payment.transaction'].create({
            'provider_id': provider.id,
            'contract_id': self.id,
            'amount': self.amount_total, # Asume que el contrato tiene un campo amount_total
            'state': 'pending',
        })

        # Llama al conector agnóstico
        connector = AgnosticPaymentConnector(provider)
        response = connector.process_payment(transaction)

        # Procesa la respuesta
        if response.get('status') == 'success':
            transaction.write({
                'state': 'done',
                'provider_reference': response.get('provider_transaction_id'),
            })
            self._create_payment_from_transaction(transaction)
            self.message_post(body=_("Pago exitoso a través de %s. Referencia: %s") % (provider.name, transaction.provider_reference))
        else:
            transaction.write({'state': 'failed'})
            self.message_post(body=_("El pago a través de %s falló. Motivo: %s") % (provider.name, response.get('message')))

        return True

    def _create_payment_from_transaction(self, transaction):
        """Crea un registro de account.payment a partir de una transacción exitosa."""
        self.ensure_one()
        payment_vals = {
            'date': fields.Date.context_today(self),
            'amount': transaction.amount,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'ref': f"Pago Contrato {self.name} - Ref: {transaction.reference}",
            'journal_id': transaction.provider_id.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            # En una implementación real, podrías vincular esto a una factura
            # 'reconciled_invoice_ids': [(6, 0, self.invoice_ids.filtered(lambda i: i.state == 'posted').ids)],
        }
        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()
        transaction.payment_id = payment.id
        return payment
