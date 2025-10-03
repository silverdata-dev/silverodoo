from odoo import models, fields

class SilverNetdevSystemInfoWizard(models.TransientModel):
    _name = 'silver.netdev.system.info.wizard'
    _description = 'System Info Viewer'

    info = fields.Text(string='System Information', readonly=True)
    netdev_id = fields.Many2one('silver.netdev', string='Network Device', readonly=True)
