from odoo import models, fields

class SilverdocTopic(models.Model):
    _name = 'silverdoc.topic'
    _description = 'Tema de Documentación'

    name = fields.Char('Nombre del Tema', required=True)
    module_id = fields.Many2one(
        'silverdoc.module', 
        string='Módulo', 
        required=True, 
        ondelete='cascade'
    )
    document_ids = fields.One2many(
        'silverdoc.document', 
        'topic_id', 
        string='Documentos'
    )
