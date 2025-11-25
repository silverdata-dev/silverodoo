from odoo import models, fields, api
import io, os,sys
import math
import base64
import datetime


# agrega dos niveles arriba del directorio actual
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from pruebadocs import main


def afloat(value):
    try:
        f=  float(value)
        if math.isnan(f): return 0
        return f
    except ValueError:
        return 0.0


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
            #return
            # Presuponiendo columnas -> AJUSTA TÚ los nombres reales
            idcliente = row.get("ID CLIENTE")
            partner_name = row.get("CLIENTE")

            if isinstance(partner_name, float): return
            #if math.isnan(partner_name): return 0


            # --- 5a. Buscar o crear cliente ---
            partner = None
            if idcliente:
                partner = self.env['res.partner'].search([('idcliente', '=', (idcliente))], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': partner_name or "Cliente sin nombre",
                    'idcliente': idcliente,
                })





            vendedor_name = str(row.get('VENDEDOR', '')).strip()
            zona_name = str(row.get('ZONA', '')).strip()
            instalador_name = str(row.get('INSTALADOR', '')).strip()


            # Get or create related records
            vendedor = self.env['res.users'].search([('name', '=', vendedor_name)], limit=1)
            if not vendedor:
                #_logger.warning(f"Vendedor no encontrado: '{vendedor_name}'. Se omitirá.")
                print(("no vendedor", vendedor_name))

            zona = self.env['silver.zone'].search([('name', '=', zona_name)], limit=1)
            if not zona and zona_name:
                zona = self.env['silver.zone'].create({'name': zona_name})

            instalador = self.env['res.partner'].search([('name', '=', instalador_name), ('supplier_rank', '>', 0)], limit=1)
            if not instalador and instalador_name:
                instalador = self.env['res.partner'].create({'name': instalador_name, 'supplier_rank': 1})

            # Calculate payments
            try:
                pago_efectivo = afloat(row.get('PAGO EN EFECTIVO', 0) or 0)
            except (ValueError, TypeError):
                pago_efectivo = 0
            try:
                pago_movil = afloat(row.get('PAGO MOVIL', 0) or 0)
            except (ValueError, TypeError):
                pago_movil = 0
            monto_pagado = pago_efectivo + pago_movil



            # Prepare lead values
            lead_data = {
                'name': partner_name.strip(),
                'partner_id': partner.id,
                'x_monto_instalacion': afloat(row.get('MONTO INSTALACIÓN', 0)),
                'x_monto_pagado': afloat(monto_pagado),
                'description': str(row.get('NOTAS', '')).strip(),
                'x_is_supervisor': str(row.get('SUPERVISOR', '')).strip().upper() == 'SI',
                'x_is_instalado': str(row.get('INSTALADO', '')).strip().upper() == 'SI',
                'x_zona_id': zona.id if zona else False,
                'user_id': vendedor.id if vendedor else False,
                'x_instalador_id': instalador.id if instalador else False,
            }

            print(("data", lead_data))

            # Update stage if installed
            if lead_data['x_is_instalado'] and stage_instalado:
                lead_data['stage_id'] = stage_instalado.id

            # Create or update lead
            lead = self.env['crm.lead'].search([('partner_id', '=', partner.id),], limit=1)
            if lead:
                lead.write(lead_data)
            else:
                self.env['crm.lead'].create(lead_data)


        stage_instalado = self.env.ref('silverlead.stage_lead_installed', raise_if_not_found=False)
        if not stage_instalado:
            print("La etapa 'Instalado' no fue encontrada. Asegúrese que el ID es 'silverlead.stage_lead_installed'")
            # You might want to create it if it doesn't exist
            # stage_instalado = self.env['crm.stage'].create({'name': 'Instalado', 'sequence': 100})

        main(back)