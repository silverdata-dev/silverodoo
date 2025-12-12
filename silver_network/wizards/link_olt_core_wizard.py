from odoo import models, fields

class LinkOltCoreWizard(models.TransientModel):
    _name = 'silver.core.link.olt.wizard'
    _description = 'Agregar OLTs a Core'

    core_id = fields.Many2one('silver.core', string='Core', required=True, readonly=True, default=lambda self: self.env.context.get('active_id'))
    olt_ids = fields.Many2many('silver.olt', string='OLTs a agregar')

    def action_link_olts(self):
        self.ensure_one()
        if self.olt_ids:
            self.olt_ids.write({'core_id': self.core_id.id})
        return {'type': 'ir.actions.act_window_close'}
