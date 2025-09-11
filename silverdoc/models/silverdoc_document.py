from odoo import models, fields

class SilverdocDocument(models.Model):
    _name = 'silverdoc.document'
    _description = 'Documento'

    name = fields.Char('Título', required=True)
    topic_id = fields.Many2one(
        'silverdoc.topic', 
        string='Tema', 
        required=True, 
        ondelete='cascade'
    )
    content = fields.Html('Contenido', sanitize_attributes=False)
    image_ids = fields.Many2many(
        'ir.attachment', 
        string="Imágenes Adjuntas",
        relation='silverdoc_document_attachment_rel',
        column1='document_id',
        column2='attachment_id'
    )
