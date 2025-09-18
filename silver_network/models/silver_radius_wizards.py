from odoo import models, fields

class SilverRadiusViewTableWizard(models.TransientModel):
    _name = 'silver.radius.view.table.wizard'
    _description = 'Wizard to show Radius table data'

    table_data = fields.Text(string='Table Data', readonly=True)
