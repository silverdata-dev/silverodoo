from odoo import models, fields

class IspRadiusViewTableWizard(models.TransientModel):
    _name = 'isp.radius.view.table.wizard'
    _description = 'Wizard to show Radius table data'

    table_data = fields.Text(string='Table Data', readonly=True)
