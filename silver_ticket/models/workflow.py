# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SilverTicketType(models.Model):
    _name = 'silver.ticket.type'
    _description = 'Tipo de Ticket (Proceso)'

    name = fields.Char(string='Nombre del Proceso', required=True)
    code = fields.Char(string='Código', required=True)
    description = fields.Text(string='Descripción')
    
    stage_config_ids = fields.One2many(
        'silver.ticket.stage.config', 
        'type_id', 
        string='Flujo de Etapas'
    )

class SilverTicketStageConfig(models.Model):
    _name = 'silver.ticket.stage.config'
    _description = 'Configuración de Etapa por Tipo'
    _order = 'sequence, id'

    name = fields.Char(string='Descripción del Paso', required=True)
    type_id = fields.Many2one('silver.ticket.type', string='Proceso', ondelete='cascade')
    sequence = fields.Integer(string='Secuencia', default=10)
    
    # Mapeo a la etapa real del sistema de Helpdesk (estado)
    helpdesk_stage_id = fields.Many2one(
        'helpdesk.ticket.stage', 
        string='Etapa Helpdesk (Estado)', 
        required=True
    )
    
    # Control de Acceso
    group_id = fields.Many2one(
        'res.groups', 
        string='Rol Requerido',
        help="Si se especifica, solo los usuarios de este grupo pueden mover el ticket a esta etapa."
    )
    
    # Automatización (Scripting)
    action_id = fields.Many2one(
        'ir.actions.server', 
        string='Ejecutar Acción al Entrar', 
        domain=[('model_id.model', '=', 'silver.ticket')],
        help="Acción de servidor (Python) que se ejecutará automáticamente al entrar en esta etapa."
    )
