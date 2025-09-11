from odoo import models, fields

class SilverdocModule(models.Model):
    _name = 'silverdoc.module'
    _description = 'Módulo de Documentación'

    name = fields.Char('Nombre del Módulo', required=True)
    project_id = fields.Many2one(
        'project.project', 
        string='Proyecto', 
        required=True, 
        ondelete='cascade'
    )
    topic_ids = fields.One2many(
        'silverdoc.topic', 
        'module_id', 
        string='Temas'
    )
