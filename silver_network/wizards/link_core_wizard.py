from odoo import models, fields

class LinkCoreWizard(models.TransientModel):
    _name = 'silver.node.link.core.wizard'
    _description = 'Agregar Cores a Nodo'

    node_id = fields.Many2one('silver.node', string='Node', required=True, readonly=True, default=lambda self: self.env.context.get('active_id'))
    core_ids = fields.Many2many('silver.core', string='Cores a agregar')

    def action_link_cores(self):
        self.ensure_one()
        if self.core_ids:
            self.core_ids.write({'node_id': self.node_id.id})
        return {'type': 'ir.actions.act_window_close'}
