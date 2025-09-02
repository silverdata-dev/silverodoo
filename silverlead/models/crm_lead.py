# -*- coding: utf-8 -*-
from odoo import models, fields, api
import pandas as pd
import logging

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_id_cliente = fields.Char('ID Cliente')
    x_zona_id = fields.Many2one('silverlead.zona', string='Zona')
    x_instalador_id = fields.Many2one('res.partner', string='Instalador', domain="[('supplier_rank', '>', 0)]")
    x_is_supervisor = fields.Boolean('Supervisor')
    x_is_instalado = fields.Boolean('Instalado')
    x_monto_instalacion = fields.Monetary('Monto Instalación', currency_field='company_currency')
    x_monto_pagado = fields.Monetary('Monto Pagado', currency_field='company_currency')

    _sql_constraints = [
        ('x_id_cliente_uniq', 'unique (x_id_cliente)', 'El ID de Cliente debe ser único.')
    ]

    @api.model
    def back(self, df):
        # Ensure pandas is available
        try:
            import pandas as pd
        except ImportError:
            _logger.error("Pandas library is not installed.")
            return

        stage_instalado = self.env.ref('silverlead.stage_lead_installed', raise_if_not_found=False)
        if not stage_instalado:
            _logger.error("La etapa 'Instalado' no fue encontrada. Asegúrese que el ID es 'silverlead.stage_lead_installed'")
            # You might want to create it if it doesn't exist
            # stage_instalado = self.env['crm.stage'].create({'name': 'Instalado', 'sequence': 100})

        for index, row in df.iterrows():
            # Clean and get identifiers
            id_cliente = str(row.get('ID CLIENTE', '')).strip()
            vendedor_name = str(row.get('VENDEDOR', '')).strip()
            zona_name = str(row.get('ZONA', '')).strip()
            instalador_name = str(row.get('INSTALADOR', '')).strip()

            if not id_cliente:
                continue

            # Get or create related records
            vendedor = self.env['res.users'].search([('name', '=', vendedor_name)], limit=1)
            if not vendedor:
                _logger.warning(f"Vendedor no encontrado: '{vendedor_name}'. Se omitirá.")

            zona = self.env['silverlead.zona'].search([('name', '=', zona_name)], limit=1)
            if not zona and zona_name:
                zona = self.env['silverlead.zona'].create({'name': zona_name})

            instalador = self.env['res.partner'].search([('name', '=', instalador_name), ('supplier_rank', '>', 0)], limit=1)
            if not instalador and instalador_name:
                instalador = self.env['res.partner'].create({'name': instalador_name, 'supplier_rank': 1})

            # Calculate payments
            try:
                pago_efectivo = float(row.get('PAGO EN EFECTIVO', 0) or 0)
            except (ValueError, TypeError):
                pago_efectivo = 0
            try:
                pago_movil = float(row.get('PAGO MOVIL', 0) or 0)
            except (ValueError, TypeError):
                pago_movil = 0
            monto_pagado = pago_efectivo + pago_movil

            # Prepare lead values
            lead_data = {
                'name': str(row.get('CLIENTE', 'Sin Nombre')).strip(),
                'x_id_cliente': id_cliente,
                'x_monto_instalacion': float(row.get('MONTO INSTALACIÓN', 0) or 0),
                'x_monto_pagado': monto_pagado,
                'description': str(row.get('NOTAS', '')).strip(),
                'x_is_supervisor': str(row.get('SUPERVISOR', '')).strip().upper() == 'SI',
                'x_is_instalado': str(row.get('INSTALADO', '')).strip().upper() == 'SI',
                'x_zona_id': zona.id if zona else False,
                'user_id': vendedor.id if vendedor else False,
                'x_instalador_id': instalador.id if instalador else False,
            }

            # Update stage if installed
            if lead_data['x_is_instalado'] and stage_instalado:
                lead_data['stage_id'] = stage_instalado.id

            # Create or update lead
            lead = self.search([('x_id_cliente', '=', id_cliente)], limit=1)
            if lead:
                lead.write(lead_data)
            else:
                self.create(lead_data)
        
        _logger.info("Proceso de importación/actualización de leads completado.")
