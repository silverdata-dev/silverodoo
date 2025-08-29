
import logging
from odoo import models, fields, api
import requests
import json


_logger = logging.getLogger(__name__)

class SendTemplateWizard(models.TransientModel):
    _name = 'silveremail.send_template_wizard'
    _description = 'Wizard para Enviar Template a Clientes'

    template_name = fields.Char(string='Nombre del Template', required=True)

    def action_send_template(self):
        self.ensure_one()
        partner_ids = self.env.context.get('active_ids', [])
        partners = self.env['res.partner'].browse(partner_ids)

        url = "https://api.zeptomail.com/v1.1/email/template/batch"

        _logger.info(f"Botón 'Enviar' presionado.")
        _logger.info(f"Template a usar: {self.template_name}")
        _logger.info(f"Procesando {len(partners)} clientes seleccionados.")
        _logger.info(f"IDs de clientes: {[p.id for p in partners]}")

        lista = json.dumps( [{"email_address": {"address": p.email,"name": p.name},
                              "merge_info": {"name":"name_valueluis","team":"team_valueluis","product_name":"Luis producto"}}

                              for p in partners])


        payload = '''
        {\n\"mail_template_key\":\"2d6f.6ea5ff3994a2d856.k1.1c0b4101-834f-11f0-9f35-fae9afc80e45.198ebda890f\",
        \n\"from\": { \"address\": \"noreply@silver-data.net\", \"name\": \"No responder\"},
        \n\"to\": '''+ lista + '''
        }'''

        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'authorization': "Zoho-enczapikey wSsVR61/+BL4Dq8vmDyrdOc7nA9dBlv1HUh+2Qbw4yWoTarDpsc/kxWfAwHyGPRKFjRqEDVE8e4rnEpUhDQIh9h8nFgECyiF9mqRe1U4J3x17qnvhDzPVm5VmxaMKIILzg9vnGFpEcsi+g==",
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        print(response.text)

        # --- INICIO DE TU CÓDIGO ---
        # Aquí puedes agregar tu lógica para procesar la lista de 'partners'.
        # Por ejemplo, buscar la plantilla y enviar los correos.
        #
        # for partner in partners:
        #     _logger.info(f"Procesando a {partner.name}...")
        #
        # --- FIN DE TU CÓDIGO ---

        return {'type': 'ir.actions.act_window_close'}
