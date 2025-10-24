# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, route

_logger = logging.getLogger(__name__)

class PaymentGatewayController(http.Controller):

    @route('/payment/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def payment_webhook(self):
        """
        Endpoint para recibir notificaciones de la pasarela de pago.
        Se espera un JSON con los datos del pago.
        """
        data = request.jsonrequest
        _logger.info("Notificación de pago recibida: %s", json.dumps(data, indent=2))

        # --- LÓGICA DE EJEMPLO ---
        # Aquí deberás adaptar el código para extraer los datos reales que envíe tu pasarela.
        # Por ejemplo:
        # 'reference': La referencia del pago (ej. "00123456")
        # 'amount': El monto del pago
        # 'journal_code': Un código para identificar el diario/banco (ej. "BDV", "PM")
        # 'partner_ref': El RIF o CI del cliente para buscarlo
        
        payment_ref = data.get('reference')
        amount = data.get('amount')
        journal_code = data.get('journal_code')
        partner_ref = data.get('partner_ref')

        if not all([payment_ref, amount, journal_code, partner_ref]):
            _logger.error("Datos incompletos en el webhook: %s", data)
            return {'status': 'error', 'message': 'Datos incompletos'}

        try:
            # Buscar el diario (banco) por su código corto
            journal = request.env['account.journal'].sudo().search([('code', '=', journal_code)], limit=1)
            if not journal:
                raise ValueError(f"Diario con código '{journal_code}' no encontrado.")

            # Buscar al cliente por su RIF/CI
            partner = request.env['res.partner'].sudo().search([('vat', '=', partner_ref)], limit=1)
            if not partner:
                raise ValueError(f"Cliente con RIF/CI '{partner_ref}' no encontrado.")

            # Crear el pago en Odoo
            payment_vals = {
                'amount': amount,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'ref': payment_ref,
                'date': fields.Date.today(),
                'journal_id': journal.id,
                'partner_id': partner.id,
            }
            
            payment = request.env['account.payment'].sudo().create(payment_vals)
            payment.action_post()
            
            _logger.info("Pago creado exitosamente: %s", payment.name)
            
            # Opcional: Intentar conciliar con una factura
            # Esta parte es más compleja y depende de tu lógica de negocio
            
            return {'status': 'ok', 'payment_id': payment.id}

        except Exception as e:
            _logger.exception("Error al procesar el webhook de pago.")
            return {'status': 'error', 'message': str(e)}
