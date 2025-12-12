from odoo import models, fields

class LinkApWizard(models.TransientModel):
    _name = 'silver.core.link.ap.wizard'
    _description = 'Agregar APs al Core'

    core_id = fields.Many2one('silver.core', string='Core', required=True, readonly=True, default=lambda self: self.env.context.get('active_id'))
    ap_ids = fields.Many2many('silver.ap', string='APs a agregar')

    def action_link_aps(self):
        self.ensure_one()
        if self.ap_ids:
            self.ap_ids.write({'core_id': self.core_id.id})
        return {'type': 'ir.actions.act_window_close'}
