# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import librouteros

class SilverNetdevRadiusClientWizard(models.TransientModel):
    _name = 'silver.netdev.radius.client.wizard'
    _description = 'Manage MikroTik Radius Client Configuration'

    netdev_id = fields.Many2one('silver.netdev', string='Network Device', required=True)
    radius_client_ip = fields.Char(string='Radius Server IP', required=True)
    radius_client_secret = fields.Char(string='Radius Shared Secret', required=True)
    radius_client_services = fields.Many2many('silver.radius.service', string='Radius Services', default=lambda self: self.env['silver.radius.service'].search([('name', 'in', ['ppp', 'hotspot'])]))

    def action_add_update_radius_client(self):
        self.ensure_one()
        netdev = self#.netdev_id
        if not netdev:
            raise UserError(_("Network Device not linked."))

        api,e = netdev._get_api_connection()
        if api:
            try:
                existing_client = api.path('/radius').get(address=self.radius_client_ip)
                services_str = ",".join(self.radius_client_services.mapped('name')) if self.radius_client_services else ""

                if existing_client:
                    api.path('/radius').set(
                        **{'.id': existing_client[0]['.id'],
                           'secret': self.radius_client_secret,
                           'service': services_str,
                           'authentication': 'yes',
                           'accounting': 'yes'}
                    )
                    message = "Radius client updated successfully!"
                else:
                    api.path('/radius').add(
                        address=self.radius_client_ip,
                        secret=self.radius_client_secret,
                        service=services_str,
                        authentication='yes',
                        accounting='yes'
                    )
                    message = "Radius client added successfully!"
                
                netdev.write({'state': 'connected'})
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
                netdev.write({'state': 'error'})
                raise UserError(_("Failed to configure Radius client: %s") % e)
            finally:
                api.close()
        else:
            raise UserError(_("Could not connect to the MikroTik router : %s")% f"{e}", )

    def action_remove_radius_client(self):
        self.ensure_one()
        netdev = self#.netdev_id
        if not netdev:
            raise UserError(_("Network Device not linked."))

        api,e = netdev._get_api_connection()
        if api:
            try:
                existing_client = api.path('/radius').get(address=self.radius_client_ip)
                if existing_client:
                    api.path('/radius').remove(id=existing_client[0]['.id'])
                    message = "Radius client removed successfully!"
                else:
                    message = "Radius client not found for this IP."
                
                netdev.write({'state': 'connected'})
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
                netdev.write({'state': 'error'})
                raise UserError(_("Failed to remove Radius client: %s") % e)
            finally:
                api.close()
        else:
            raise UserError(_("Could not connect to the MikroTik router: %s.")%e)

    def action_view_radius_clients(self):
        self.ensure_one()
        netdev = self#.netdev_id
        if not netdev:
            raise UserError(_("Network Device not linked."))

        api = netdev._get_api_connection()
        if api:
            try:
                radius_clients = api.path('/radius').get()
                client_list = "\n".join([f"Address: {client.get('address')}, Secret: {client.get('secret')}, Services: {client.get('service')}" for client in radius_clients])
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'MikroTik Radius Clients',
                        'message': client_list if client_list else "No Radius clients found.",
                        'type': 'info',
                        'sticky': True,
                    }
                }
            except Exception as e:
                netdev.write({'state': 'error'})
                raise UserError(_("Failed to retrieve Radius clients: %s") % e)
            finally:
                api.close()
        else:
            raise UserError(_("Could not connect to the MikroTik router."))