from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import pyrad.packet

class SilverRadius(models.Model):
    _inherit = 'silver.radius'

    def action_disconnect_session(self, username, nas_identifier):
        self.ensure_one()
        if not self.nas_address or not self.nas_secret:
            raise UserError(_("NAS Address and Secret are required."))

        srv = Client(server=self.nas_address,
                     secret=self.nas_secret.encode('utf-8'),
                     dict=Dictionary("dictionary"))

        # Create a disconnect request packet
        req = srv.CreateCoAPacket(
            code=pyrad.packet.DisconnectRequest,
            User_Name=username,
            NAS_Identifier=nas_identifier
        )

        try:
            # Send the packet and wait for a reply
            reply = srv.SendPacket(req)

            if reply.code == pyrad.packet.DisconnectACK:
                message = "Disconnect ACK received."
            else:
                message = f"Disconnect NAK received: {reply.get('Error-Cause', ['Unknown error'])[0]}"

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': message,
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Failed to send disconnect request: %s") % e)

    def action_open_disconnect_wizard(self):
        self.ensure_one()
        return {
            'name': _('Disconnect/CoA Request'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.radius.disconnect.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_radius_id': self.id},
        }

    def action_send_coa_request(self, username, nas_identifier, attributes=None):
        self.ensure_one()
        if not self.nas_address or not self.nas_secret:
            raise UserError(_("NAS Address and Secret are required."))

        srv = Client(server=self.nas_address,
                     secret=self.nas_secret.encode('utf-8'),
                     dict=Dictionary("dictionary"))

        # Create a CoA request packet
        req = srv.CreateCoAPacket(
            code=pyrad.packet.CoARequest,
            User_Name=username,
            NAS_Identifier=nas_identifier
        )

        if attributes:
            for attr, value in attributes.items():
                req[attr] = value

        try:
            # Send the packet and wait for a reply
            reply = srv.SendPacket(req)

            if reply.code == pyrad.packet.CoAACK:
                message = "CoA ACK received."
            else:
                message = f"CoA NAK received: {reply.get('Error-Cause', ['Unknown error'])[0]}"

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': message,
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Failed to send CoA request: %s") % e)
