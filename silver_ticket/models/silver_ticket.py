# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SilverTicket(models.Model):
    _name = 'silver.ticket'
    _inherit = 'helpdesk.ticket'

    ticket_type = fields.Selection([
        ('failure', 'Caída de Conexión'),
        ('slow_speed', 'Lentitud'),
        ('billing', 'Facturación'),
        ('installation', 'Instalación'),
        ('other', 'Otro'),
    ], string='Tipo de Ticket (Legacy)', default='failure')

    ticket_type_id = fields.Many2one('silver.ticket.type', string="Categoría/Proceso", help="Define el flujo de trabajo automatizado")

    contract_id = fields.Many2one('silver.contract', string='Contrato')
    partner_id = fields.Many2one(related='contract_id.partner_id', store=True)

    def write(self, vals):
        # 1. Verificación de Permisos (Antes de guardar)
        if 'stage_id' in vals:
            new_stage_id = vals['stage_id']
            for ticket in self:
                if ticket.ticket_type_id:
                    # Buscar configuración para esta etapa en este tipo de proceso
                    config = self.env['silver.ticket.stage.config'].search([
                        ('type_id', '=', ticket.ticket_type_id.id),
                        ('helpdesk_stage_id', '=', new_stage_id)
                    ], limit=1)
                    
                    if config and config.group_id:
                        if config.group_id not in self.env.user.groups_id:
                            raise models.UserError(
                                f"No tienes permiso para mover este ticket a '{config.name}'. "
                                f"Se requiere el rol: {config.group_id.name}"
                            )

        # 2. Guardar cambios
        res = super(SilverTicket, self).write(vals)

        # 3. Ejecutar Acciones Automáticas (Después de guardar)
        if 'stage_id' in vals:
            new_stage_id = vals['stage_id']
            for ticket in self:
                if ticket.ticket_type_id:
                    config = self.env['silver.ticket.stage.config'].search([
                        ('type_id', '=', ticket.ticket_type_id.id),
                        ('helpdesk_stage_id', '=', new_stage_id)
                    ], limit=1)

                    if config and config.action_id:
                        # Ejecutar Server Action
                        # Pasamos el ticket actual como 'record' en el contexto
                        config.action_id.with_context(
                            active_id=ticket.id,
                            active_ids=[ticket.id],
                            active_model='silver.ticket'
                        ).run()
        
        return res
