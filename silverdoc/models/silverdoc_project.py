from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    doc_module_ids = fields.One2many(
        'silverdoc.module',
        'project_id',
        string='Módulos de Documentación'
    )
