# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SilverOltDiscoveredOnu(models.Model):
    _name = 'silver.olt.discovered.onu'
    _description = 'ONU Descubierta No Registrada en OLT'
    _order = 'olt_index'
    _rec_name = 'name'

    name = fields.Char(
        string='Nombre', 
        compute='_compute_display_name', 
        store=True, 
        readonly=True
    )
    olt_id = fields.Many2one(
        'silver.olt', 
        string='OLT', 
        required=True, 
        ondelete='cascade'
    )
    display_name = fields.Char(string='Display Name', related='name')
    olt_index = fields.Char(string='Índice OLT', readonly=True)
    serial_number = fields.Char(string='Serial (SN)', readonly=True, index=True)
    password = fields.Char(string='Password (PW)', readonly=True)
    loid = fields.Char(string='LOID', readonly=True)
    model_name = fields.Char(string='Modelo', readonly=True)
    version = fields.Char(string='Versión', readonly=True)
    loid_password = fields.Char(string='LOID Password', readonly=True)

    # GEMINI: Campos para gestionar la asignación a un contrato
    is_assigned = fields.Boolean(
        string='Asignada', 
        default=False, 
        index=True,
        help="Indica si esta ONU ya ha sido asignada a un contrato."
    )
    contract_id = fields.Many2one(
        'silver.contract', 
        string='Contrato Asignado', 
        readonly=True,
        help="Contrato al que esta ONU ha sido asignada."
    )

    @api.depends('olt_index', 'serial_number', 'model_name')
    def _compute_display_name(self):
        for record in self:
            record.name = f"[{record.olt_index or ''}] SN: {record.serial_number or ''} Modelo: {record.model_name or ''}"

    _sql_constraints = [
        ('olt_index_uniq', 'unique (olt_id, olt_index)',
         'El olt_index de la ONU debe ser único por cada OLT.')
    ]
