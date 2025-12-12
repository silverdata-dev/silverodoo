from odoo import models, fields

class LinkNodeWizard(models.TransientModel):
    _name = 'silver.zone.link.node.wizard'
    _description = 'Agregar Nodos a Zona'

    zone_id = fields.Many2one('silver.zone', string='Zona', required=True, readonly=True, default=lambda self: self.env.context.get('active_id'))
    node_ids = fields.Many2many('silver.node', string='Nodos a agregar')

    def action_link_nodes(self):
        self.ensure_one()
        if self.node_ids:
            self.node_ids.write({'zone_id': self.zone_id.id})
        return {'type': 'ir.actions.act_window_close'}
