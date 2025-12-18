# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError




class SilverKexAlgorithms(models.Model):
    _name = 'silver.kex.algorithms'
    _description = 'Placeholder for Silver Kex Algorithms'
    name = fields.Char('Name')


class AddressListChannelLine(models.Model):
    _name = 'address.list.channel.line'
    _description = 'Placeholder for Address List Channel Line'
    name = fields.Char('Name')
    core_id = fields.Many2one('silver.core', string='Router')


class SilverCorePortLine(models.Model):
    _name = 'silver.core.port.line'
    _description = 'Placeholder for Port Line'
    name = fields.Char('Name')
    core_id = fields.Many2one('silver.core', string='Router')

class OltLineProduct(models.Model):
    _name = 'olt.line.product'
    _description = 'OLT Line Product'
    name = fields.Char('Name')
    olt_id = fields.Many2one('silver.olt', string='OLT')

class SilverOltUsers(models.Model):
    _name = 'silver.olt.users'
    _description = 'Silver OLT Users'
    name = fields.Char('Name')
    olt_id = fields.Many2one('silver.olt', string='OLT')

class SilverTr069(models.Model):
    _name = 'silver.tr.069'
    _description = 'Silver TR-069 Server'
    name = fields.Char('Name')
    description = fields.Text('Description')
    url = fields.Text('Url')

class SilverOnuLine(models.Model):
    _name = 'silver.onu.line'
    _description = 'Silver ONU Line'
    name = fields.Char('Name')
    box_id = fields.Many2one('silver.box', string='Box')


class DevicePoolIp(models.Model):
    _name = 'silver.device.pool.ip'
    _description = 'Device Pool IP'
    name = fields.Char('Name')
    ap_id = fields.Many2one('silver.ap', string='AP')




class SilverDeviceNetworks(models.Model):
    _name = 'silver.device.networks'
    _description = 'Silver Device Networks'
    name = fields.Char('Name')
    core_id = fields.Many2one('silver.core', string='Router')
    olt_id = fields.Many2one('silver.olt', string='OLT')
    card_id = fields.Many2one('silver.olt.card', string='Card')
    port_id = fields.Many2one('silver.olt.card.port', string='Port')
    #radius_id = fields.Many2one('silver.radius', string='Radius')
    is_tr_069 = fields.Boolean('Is TR-069')
