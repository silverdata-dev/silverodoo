# -*- coding: utf-8 -*-
from odoo import models, fields

class SilverContract(models.Model):
    _inherit = 'silver.contract'

    # Añadimos los campos específicos para la gestión de ISP al modelo existente
    recurring_template_id = fields.Many2one(
        'recurring.template', 
        string='Plantilla de Facturación',
        help="Plantilla que genera la factura mensual para este contrato."
    )

    equipment_ids = fields.One2many('isp.equipment', 'contract_id', string='Equipos Instalados')
