# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import librouteros

class IspRadiusNasWizard(models.TransientModel):
    _name = 'isp.radius.nas.wizard'
    _description = 'Manage MikroTik NAS Clients'

    radius_id = fields.Many2one('isp.radius', string='Radius Server', required=True)
    nas_address = fields.Char(string='NAS Address', required=True)
    nas_secret = fields.Char(string='NAS Secret', required=True)
    nas_services = fields.Many2many('isp.radius.service', string='Services', default=lambda self: self.env['isp.radius.service'].search([('name', 'in', ['ppp', 'hotspot'])]))

    def action_add_nas_client(self):
        self.ensure_one()
        radius_server = self.radius_id
        if not radius_server.netdev_id:
            raise UserError(_("The selected Radius server is not linked to a Network Device."))

        api = radius_server.netdev_id._get_api_connection()
        if api:
            try:
                existing_nas = api.path('/radius').get(address=self.nas_address)
                services_str = ",".join(self.nas_services.mapped('name')) if self.nas_services else ""

                if existing_nas:
                    raise UserError(_("NAS client with this address already exists on the MikroTik router."))

                api.path('/radius').add(
                    address=self.nas_address,
                    secret=self.nas_secret,
                    service=services_str,
                    authentication='yes',
                    accounting='yes'
                )
                radius_server.netdev_id.write({'state': 'connected'})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': 'NAS client added successfully!',
                        'type': 'success',
                    }
                }
            except Exception as e:
                radius_server.netdev_id.write({'state': 'error'})
                raise UserError(_("Failed to add NAS client: %s") % e)
            finally:
                api.close()
        else:
            raise UserError(_("Could not connect to the MikroTik router."))

    def action_remove_nas_client(self):
        self.ensure_one()
        radius_server = self.radius_id
        if not radius_server.netdev_id:
            raise UserError(_("The selected Radius server is not linked to a Network Device."))

        api = radius_server.netdev_id._get_api_connection()
        if api:
            try:
                existing_nas = api.path('/radius').get(address=self.nas_address)
                if not existing_nas:
                    raise UserError(_("NAS client with this address not found on the MikroTik router."))

                api.path('/radius').remove(id=existing_nas[0]['.id'])
                radius_server.netdev_id.write({'state': 'connected'})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': 'NAS client removed successfully!',
                        'type': 'success',
                    }
                }
            except Exception as e:
                radius_server.netdev_id.write({'state': 'error'})
                raise UserError(_("Failed to remove NAS client: %s") % e)
            finally:
                api.close()
        else:
            raise UserError(_("Could not connect to the MikroTik router."))

    def action_view_nas_clients(self):
        self.ensure_one()
        radius_server = self.radius_id
        if not radius_server.netdev_id:
            raise UserError(_("The selected Radius server is not linked to a Network Device."))

        api = radius_server.netdev_id._get_api_connection()
        if api:
            try:
                nas_clients = api.path('/radius').get()
                # This part would typically populate a temporary model or a list for display
                # For simplicity, we'll just return a notification with the list
                nas_list = "\n".join([f"Address: {nas.get('address')}, Secret: {nas.get('secret')}, Services: {nas.get('service')}" for nas in nas_clients])
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'MikroTik NAS Clients',
                        'message': nas_list if nas_list else "No NAS clients found.",
                        'type': 'info',
                        'sticky': True,
                    }
                }
            except Exception as e:
                radius_server.netdev_id.write({'state': 'error'})
                raise UserError(_("Failed to retrieve NAS clients: %s") % e)
            finally:
                api.close()
        else:
            raise UserError(_("Could not connect to the MikroTik router."))
