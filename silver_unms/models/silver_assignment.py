# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SilverAssignment(models.Model):
    _name = 'silver.assignment'
    _description = 'Asignación'
    _rec_name = 'display_name'

    name = fields.Char(string='Nombre', store=True)
    display_name = fields.Char(string='Nombre Mostrado', compute='_compute_name', store=True)

    active = fields.Boolean(string='Activo', default=True)
    user_id = fields.Many2one('res.users', string='Instalador/Usuario', required=False)
    zone_ids = fields.Many2many('silver.zone', string='Zonas Permitidas')
    node_ids = fields.Many2many(
        'silver.node',
        string='Nodos Permitidos',
        domain="[('zone_id', 'in', zone_ids)]"
    )
    
    # Color para identificar al instalador en el calendario
    color = fields.Integer(string='Color')

    @api.depends('user_id', 'zone_ids')
    def _compute_name(self):
        for rec in self:
            if rec.user_id:
                # Mostramos solo el nombre del usuario
               # rec.name = rec.user_id.name
                rec.display_name = rec.user_id.name
            else:
                rec.name = "Sin Asignar"
                rec.display_name = "Sin Asignar"

    @api.model_create_multi
    def create(self, vals_list):
        record = super(SilverAssignment, self).create(vals_list)
        
        # --- GHOST MODE (MODO FANTASMA) ---
        # web_timeline ignora 'group_expand', por lo que si un grupo no tiene registros, desaparece.
        # Creamos un registro "Placeholder" en el pasado lejano para forzar la aparición de la fila.
        self.env['crm.lead'].create({
            'name': f"[System] {record.display_name or 'Instalador'} - Placeholder",
            'type': 'opportunity',
            'assignment_id': record.id,
            'user_id': record.user_id.id if record.user_id else False,
            'schedule_start': '1980-01-01 08:00:00',
            'schedule_stop': '1980-01-01 09:00:00',
            'probability': 0,
            'active': True,
            'description': 'Registro técnico para inicializar la fila en el Timeline. No borrar.'
        })
        # ----------------------------------

        return record

    def unlink(self):
        # Limpieza: Borrar los leads fantasma asociados al eliminar la asignación
        for record in self:
            # Buscamos específicamente el placeholder creado por el sistema
            self.env['crm.lead'].search([
                ('assignment_id', '=', record.id),
                ('schedule_start', '=', '1980-01-01 08:00:00'),
                ('active', 'in', [True, False]) # Buscar incluso si fue archivado
            ]).unlink()
        return super(SilverAssignment, self).unlink()
