# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    schedule_start = fields.Datetime(string="Inicio Agenda", index=True)
    schedule_stop = fields.Datetime(string="Fin Agenda", index=True)
    
    # Campo relacionado almacenado para información
    zone_id = fields.Many2one(
        'silver.zone',
        string="Zona",
        related='silver_address_id.zone_id',
        store=True,
        readonly=True
    )
    
    # Nuevo campo para el eje Y del calendario
    assignment_id = fields.Many2one(
        'silver.assignment', 
        string="Asignación (Instalador)",
        group_expand='_read_group_assignment_ids',
        index=True
    )

    @api.model
    def _read_group_assignment_ids(self, assignments, domain, order):
        """
        Esta función permite mostrar TODOS los registros de silver.assignment activos en el eje Y,
        incluso si no tienen oportunidades asignadas en el periodo actual.
        """
        print("DEBUG: _read_group_assignment_ids called")
        # Ignoramos el 'domain' de crm.lead porque queremos listar todas las asignaciones activas
        # como cabeceras, independientemente de si tienen oportunidades en el dominio actual.
        search_domain = [('active', '=', True)]
        a = self.env['silver.assignment'].search(search_domain, order=order)
        print(("DEBUG2 ", a))
        return a

    @api.onchange('schedule_start')
    def _onchange_schedule_start(self):
        """Si se establece una fecha de inicio y no hay fecha de fin, 
        se sugiere 2 hora de duración por defecto para instalaciones."""
        if self.schedule_start and not self.schedule_stop:
            self.schedule_stop = self.schedule_start + timedelta(hours=2)

    @api.onchange('user_id')
    def _onchange_user_id_assignment(self):
        """
        Intenta asignar automáticamente el silver.assignment correspondiente 
        cuando se selecciona un user_id en el lead.
        """
        if self.user_id:
            assignment = self.env['silver.assignment'].search([('user_id', '=', self.user_id.id)], limit=1)
            if assignment:
                self.assignment_id = assignment.id

    @api.onchange('node_id')
    def _onchange_node_id_assignment(self):
        """
        Cuando cambia el nodo, busca un instalador (assignment) que cubra la zona del nodo.
        """
        if self.node_id and self.node_id.zone_id:
            assignment = self.env['silver.assignment'].search([
                '|', ('node_ids', 'in', self.node_id.id),
                ('zone_ids', 'in', self.node_id.zone_id.id),
                ('active', '=', True)
            ], limit=1)
            if assignment:
                self.assignment_id = assignment.id

    def write(self, vals):
        """
        Sobrescribimos write para sincronizar user_id si se cambia assignment_id desde el timeline,
        y asegurar consistencia de fechas.
        """
        if 'assignment_id' in vals:
            assignment = self.env['silver.assignment'].browse(vals['assignment_id'])
            if assignment and assignment.user_id:
                 vals['user_id'] = assignment.user_id.id

        return super(CrmLead, self).write(vals)
