from odoo import models, fields

class LinkOltWizard(models.TransientModel):
    _name = 'silver.node.link.olt.wizard'
    _description = 'Agregar OLTs a Nodo'

    node_id = fields.Many2one('silver.node', string='Nodo', required=True, readonly=True, default=lambda self: self.env.context.get('active_id'))
    olt_ids = fields.Many2many('silver.olt', string='OLTs a agregar')

    def action_link_olts(self):
        self.ensure_one()
        if self.olt_ids:
            self.olt_ids.write({'node_id': self.node_id.id})
        return {'type': 'ir.actions.act_window_close'}
