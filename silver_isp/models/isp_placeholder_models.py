from odoo import models, fields

class IspRadius(models.Model):
    _name = 'isp.radius'
    _description = 'Placeholder for ISP Radius'
    name = fields.Char('Name')

class IspDeviceNetworks(models.Model):
    _name = 'isp.device.networks'
    _description = 'Placeholder for ISP Device Networks'
    name = fields.Char('Name')

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

class IspIpAddressLine(models.Model):
    _name = 'isp.ip.address.line'
    _description = 'Placeholder for ISP IP Address Line'
    name = fields.Char('Name')
    core_id = fields.Many2one('isp.core', string='Core')

class IspIpAddress(models.Model):
    _name = 'isp.ip.address'
    _description = 'Placeholder for ISP IP Address'
    name = fields.Char('Name')
    core_id = fields.Many2one('isp.core', string='Core')

class IspCorePortLine(models.Model):
    _name = 'isp.core.port.line'
    _description = 'Placeholder for ISP Core Port Line'
    name = fields.Char('Name')
    core_id = fields.Many2one('isp.core', string='Core')

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Placeholder for Product Brand'
    name = fields.Char('Name')
    description = fields.Text('Description')
