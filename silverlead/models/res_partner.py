from odoo import models, fields, api
import io, os,sys
import base64
import datetime


# agrega dos niveles arriba del directorio actual
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from pruebadocs import main


class ResPartner(models.Model):
    _inherit = 'res.partner'

    idcliente = fields.Char(string="ID Cliente", index=True, tracking=True)

    @api.model
    def _cron_import_data(self):
        """
        Este es el método que ejecutará el cron diariamente.
        Aquí debes añadir tu lógica para la importación de datos.
        """
        # EJEMPLO:
        # partners_to_update = self.search([(some_condition)])
        # for partner in partners_to_update:
        #     # ... lógica de importación ...
        #     _logger.info(f"Importando datos para el cliente {partner.name}")
        
        # DEJA TU CÓDIGO DE IMPORTACIÓN AQUÍ
        def back(row):
            print(row)
            return
            # Presuponiendo columnas -> AJUSTA TÚ los nombres reales
            partner_id = row.get("ClienteID")
            partner_name = row.get("NombreCliente")
            partner_email = row.get("Email")
            lead_name = row.get("Oportunidad")
            lead_stage = row.get("Etapa")  # p.ej. 'New', 'Won', etc.

            # --- 5a. Buscar o crear cliente ---
            partner = None
            if partner_id:
                partner = self.env['res.partner'].search([('id', '=', int(partner_id))], limit=1)
            if not partner and partner_email:
                partner = self.env['res.partner'].search([('email', '=', partner_email)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': partner_name or "Cliente sin nombre",
                    'email': partner_email,
                })

            # --- 5b. Buscar o crear lead ligado al cliente ---
            lead = self.env['crm.lead'].search([
                ('partner_id', '=', partner.id),
                ('name', '=', lead_name)
            ], limit=1)

            if lead:
                # actualizar etapa
                stage = self.env['crm.stage'].search([('name', '=', lead_stage)], limit=1)
                if stage:
                    lead.stage_id = stage.id
            else:
                stage = self.env['crm.stage'].search([('name', '=', lead_stage)], limit=1)
                self.env['crm.lead'].create({
                    'name': lead_name,
                    'partner_id': partner.id,
                    'stage_id': stage.id if stage else False,
                })


        main(back)