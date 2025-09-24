# -*- coding: utf-8 -*-
from odoo import models, fields

class ContractTemplateWp(models.Model):
    _name = 'contract.template.wp'
    _description = 'Plantilla de WhatsApp'

    name = fields.Char(string='Nombre', required=True)
    content = fields.Text(string='Contenido')
