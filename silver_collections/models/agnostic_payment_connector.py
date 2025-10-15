# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class AgnosticPaymentConnector:
    """
    Clase agnóstica para procesar pagos a través de una API externa.
    """

    def __init__(self, provider):
        self.provider = provider

    def _prepare_payment_data(self, transaction):
        """
        Prepara el diccionario de datos para la API a partir de la transacción.
        """
        return {
            'transaction_id': transaction.reference,
            'customer_name': transaction.contract_id.partner_id.name,
            'customer_vat': transaction.contract_id.partner_id.vat,
            'amount': transaction.amount,
            'currency': transaction.currency_id.name,
            'description': f"Pago de Contrato {transaction.contract_id.name}",
        }

    def process_payment(self, transaction):
        """
        Procesa el pago. Este es el método que debes modificar en el futuro.
        """
        payload = self._prepare_payment_data(transaction)
        transaction.raw_request = json.dumps(payload, indent=2)
        _logger.info("Procesando pago (simulado) para la transacción %s", transaction.reference)

        # --- ZONA A MODIFICAR EN EL FUTURO ---
        # Aquí harías la llamada real a la API con self.provider.api_url,
        # self.provider.api_token y el payload.
        #
        # try:
        #     headers = {'Authorization': f'Bearer {self.provider.api_token}'}
        #     response = requests.post(self.provider.api_url, json=payload, headers=headers)
        #     response.raise_for_status()
        #     api_response = response.json()
        # except Exception as e:
        #     return {'status': 'failed', 'error_message': str(e)}
        # --- FIN ZONA A MODIFICAR ---

        # --- RESPUESTA SIMULADA (BORRAR EN EL FUTURO) ---
        _logger.warning("Usando respuesta de pago simulada.")
        api_response = {
            'status': 'success',
            'provider_transaction_id': f"BANK-TX-{int(datetime.now().timestamp())}",
            'message': 'Pago aprobado exitosamente por el banco de pruebas.'
        }
        # --- FIN RESPUESTA SIMULADA ---

        transaction.raw_response = json.dumps(api_response, indent=2)
        return api_response
