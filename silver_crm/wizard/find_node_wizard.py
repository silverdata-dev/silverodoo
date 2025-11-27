# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class CrmFindNodeWizard(models.TransientModel):
    _name = 'crm.find.node.wizard'
    _description = 'Asistente para Encontrar Nodos Cercanos'

    lead_id = fields.Many2one('crm.lead', string="Oportunidad", required=True, readonly=True)
    line_ids = fields.One2many('crm.find.node.wizard.line', 'wizard_id', string="Nodos Cercanos", readonly=True)
    
    # El método default_get se elimina porque la lógica ahora está en el crm.lead
    # que crea el registro antes de abrirlo.

class CrmFindNodeWizardLine(models.TransientModel):
    _name = 'crm.find.node.wizard.line'
    _description = 'Línea del Asistente de Nodos'
    _order = 'distance'

    wizard_id = fields.Many2one('crm.find.node.wizard', string="Asistente", required=True, ondelete='cascade')
    node_id = fields.Many2one('silver.node', string="Nodo", readonly=True)
    distance = fields.Float(string="Distancia (mts)", digits='Product Price', readonly=True)

    def action_select_node(self):
        """
        Asigna el nodo seleccionado a la oportunidad y cierra el asistente.
        Esto funciona porque el wizard y sus líneas ya existen en la base de datos.
        """
        self.ensure_one()
        self.wizard_id.lead_id.node_id = self.node_id.id
        return {'type': 'ir.actions.act_window_close'}
