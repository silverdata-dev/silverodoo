# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import ipaddress

class ProductBrand(models.Model):
    _name = 'product.brand'
    #_inherit = 'product.brand'
    name = fields.Char('Name')
    description = fields.Text('Description')
    partner_ids = fields.Many2many('res.partner', string='Proveedores')
    logo = fields.Binary(string='Imagen')



class IspKexAlgorithms(models.Model):
    _name = 'isp.kex.algorithms'
    _description = 'Placeholder for ISP Kex Algorithms'
    name = fields.Char('Name')

class IspVlan(models.Model):
    _name = 'isp.vlan'
    _description = 'Placeholder for ISP VLAN'
    name = fields.Char('Name')

class AddressListChannelLine(models.Model):
    _name = 'addres.list.channel.line'
    _description = 'Placeholder for Address List Channel Line'
    name = fields.Char('Name')
    core_id = fields.Many2one('isp.core', string='Core')

class IspIpAddress(models.Model):
    _name = 'isp.ip.address'
    _description = 'ISP IP Address Range'
    _order = 'name'

    name = fields.Char(string='Description', required=True)
    cidr = fields.Char(string='CIDR Notation', required=True, help="e.g., 192.168.0.0/24")
    gateway = fields.Char(string='Gateway')
    core_id = fields.Many2one('isp.core', string='Core')
    olt_id = fields.Many2one('isp.olt', string='OLT')
    card_id = fields.Many2one('isp.olt.card', string='OLT Card')
    port_id = fields.Many2one('isp.olt.card.port', string='OLT Card Port')
    radius_id = fields.Many2one('isp.radius', string='Radius Server')

    line_ids = fields.One2many('isp.ip.address.line', 'address_id', string='IP Addresses')

    total_ips = fields.Integer(compute='_compute_usage_stats', string='Total IPs')
    used_ips = fields.Integer(compute='_compute_usage_stats', string='Used IPs')
    usage_percentage = fields.Float(compute='_compute_usage_stats', string='Usage (%)', group_operator="avg")

    is_tr_069 = fields.Boolean(string="Es069")

    _sql_constraints = [
        ('cidr_uniq', 'unique (cidr)', 'This CIDR already exists!')
    ]

    @api.depends('line_ids.status')
    def _compute_usage_stats(self):
        for record in self:
            total = len(record.line_ids)
            used = len(record.line_ids.filtered(lambda r: r.status == 'used'))
            record.total_ips = total
            record.used_ips = used
            record.usage_percentage = (used / total * 100) if total > 0 else 0.0

    def action_generate_ips(self):
        for record in self:
            if record.line_ids:
                raise ValidationError(_("IPs have already been generated for this range. Please delete them first if you want to regenerate."))
            try:
                network = ipaddress.ip_network(record.cidr)
                record.gateway = str(network.network_address + 1)
                ip_vals = [{'name': str(ip), 'address_id': record.id} for ip in network.hosts()]
                self.env['isp.ip.address.line'].create(ip_vals)
            except ValueError as e:
                raise ValidationError(_("Invalid CIDR notation: %s") % e)
        return True

class IspIpAddressLine(models.Model):
    _name = 'isp.ip.address.line'
    _description = 'ISP IP Address Line'
    _order = 'ip_int asc'

    name = fields.Char(string='IP Address', required=True)
    address_id = fields.Many2one('isp.ip.address', string='IP Range', ondelete='cascade', required=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('used', 'Used'),
        ('reserved', 'Reserved')
    ], string='Status', default='available', required=True)

    assigned_to = fields.Reference(selection=[], string='Assigned To')
    description = fields.Text()

    gateway = fields.Char('Gateway')
    network_address = fields.Char('Network Address')
    broadcast_address = fields.Char('Broadcast Address')


    core_id = fields.Many2one('isp.core', string='Core')
    olt_id = fields.Many2one('isp.olt', string='OLT')
    card_id = fields.Many2one('isp.olt.card', string='Card')
    port_id = fields.Many2one('isp.olt.card.port', string='Port')
    radius_id = fields.Many2one('isp.radius', string='Radius')
    is_tr_069 = fields.Boolean(string="Es069")

    ip_int = fields.Integer(compute='_compute_ip_int', store=True, help="Technical field for sorting")
    def action_borrar_pool(self):
        # Placeholder for borrar pool action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Acción "Borrar Pool" ejecutada con éxito.',
                'type': 'success',
            }
        }

    def action_remover_gw(self):
        # Placeholder for remover gw action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Acción "Remover GW" ejecutada con éxito.',
                'type': 'success',
            }
        }

    def action_remover_ct(self):
        # Placeholder for remover ct action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Acción "Remover CT" ejecutada con éxito.',
                'type': 'success',
            }
        }

    def action_regular_pool(self):
        # Placeholder for regular pool action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Acción "Regular Pool" ejecutada con éxito.',
                'type': 'success',
            }
        }


    _sql_constraints = [
        ('ip_range_uniq', 'unique (name, address_id)', 'This IP already exists in this range!')
    ]

    @api.depends('name')
    def _compute_ip_int(self):
        for record in self:
            try:
                record.ip_int = int(ipaddress.ip_address(record.name))
            except ValueError:
                record.ip_int = 0

    def action_borrar_pool(self):
        # Placeholder for borrar pool action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Acción "Borrar Pool" ejecutada con éxito.',
                'type': 'success',
            }
        }

    def action_remover_gw(self):
        # Placeholder for remover gw action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Acción "Remover GW" ejecutada con éxito.',
                'type': 'success',
            }
        }

    def action_remover_ct(self):
        # Placeholder for remover ct action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Acción "Remover CT" ejecutada con éxito.',
                'type': 'success',
            }
        }

    def action_regular_pool(self):
        # Placeholder for regular pool action
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Acción "Regular Pool" ejecutada con éxito.',
                'type': 'success',
            }
        }

class IspCorePortLine(models.Model):
    _name = 'isp.core.port.line'
    _description = 'Placeholder for ISP Core Port Line'
    name = fields.Char('Name')
    core_id = fields.Many2one('isp.core', string='Core')

class OltLineProduct(models.Model):
    _name = 'olt.line.product'
    _description = 'OLT Line Product'
    name = fields.Char('Name')
    olt_id = fields.Many2one('isp.olt', string='OLT')

class IspOltUsers(models.Model):
    _name = 'isp.olt.users'
    _description = 'ISP OLT Users'
    name = fields.Char('Name')
    olt_id = fields.Many2one('isp.olt', string='OLT')

class IspTr069(models.Model):
    _name = 'isp.tr.069'
    _description = 'ISP TR-069 Server'
    name = fields.Char('Name')
    description = fields.Text('Description')

class IspOnuLine(models.Model):
    _name = 'isp.onu.line'
    _description = 'ISP ONU Line'
    name = fields.Char('Name')
    box_id = fields.Many2one('isp.box', string='Box')

class DevicePoolIp(models.Model):
    _name = 'device.pool.ip'
    _description = 'Device Pool IP'
    name = fields.Char('Name')
    ap_id = fields.Many2one('isp.ap', string='AP')

class IspRadiusLine(models.Model):
    _name = 'isp.radius.line'
    _description = 'ISP Radius Line'
    name = fields.Char('Name')
    radius_id = fields.Many2one('isp.radius', string='Radius')
    router_id = fields.Many2one('isp.netdev', string='Router')


class IspDeviceNetworks(models.Model):
    _name = 'isp.device.networks'
    _description = 'ISP Device Networks'
    name = fields.Char('Name')
    core_id = fields.Many2one('isp.core', string='Core')
    olt_id = fields.Many2one('isp.olt', string='OLT')
    card_id = fields.Many2one('isp.olt.card', string='Card')
    port_id = fields.Many2one('isp.olt.card.port', string='Port')
    radius_id = fields.Many2one('isp.radius', string='Radius')
    is_tr_069 = fields.Boolean('Is TR-069')
