from odoo import models, fields, api, _
from odoo.exceptions import UserError

class IspRadiusDisconnectWizard(models.TransientModel):
    _name = 'isp.radius.disconnect.wizard'
    _description = 'RADIUS Disconnect/CoA Wizard'

    radius_id = fields.Many2one('isp.radius', string='RADIUS Server', required=True)
    username = fields.Char(string='Username', required=True)
    nas_identifier = fields.Char(string='NAS Identifier', default='localhost')
    coa_attributes = fields.Text(string='CoA Attributes (JSON format)', help="Enter attributes in JSON format, e.g., {\"Session-Timeout\": 3600, \"Mikrotik-Rate-Limit\": \"1M/1M\"}")

    def action_send_disconnect_request(self):
        self.ensure_one()
        self.radius_id.action_disconnect_session(self.username, self.nas_identifier)

    def action_send_coa_request(self):
        self.ensure_one()
        if not self.coa_attributes:
            raise UserError(_("CoA Attributes cannot be empty for CoA request."))
        try:
            attributes = json.loads(self.coa_attributes)
        except json.JSONDecodeError:
            raise UserError(_("Invalid JSON format for CoA Attributes."))

        self.radius_id.action_send_coa_request(self.username, self.nas_identifier, attributes)
