from odoo import models, fields

class ProductBrand(models.Model):
    _name = 'product.brand'
    #_inherit = 'product.brand'
    name = fields.Char('Name')
    description = fields.Text('Description')
    partner_ids = fields.Many2many('res.partner', string='Proveedores')
    logo = fields.Binary(string='Imagen')

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
    gateway = fields.Char('Gateway')
    network_address = fields.Char('Network Address')
    broadcast_address = fields.Char('Broadcast Address')
    core_id = fields.Many2one('isp.core', string='Core')
    olt_id = fields.Many2one('isp.olt', string='OLT')
    card_id = fields.Many2one('isp.olt.card', string='Card')
    port_id = fields.Many2one('isp.olt.card.port', string='Port')
    radius_id = fields.Many2one('isp.radius', string='Radius')
    is_tr_069 = fields.Boolean('Is TR-069')

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


class IspIpAddress(models.Model):
    _name = 'isp.ip.address'
    _description = 'Placeholder for ISP IP Address'
    name = fields.Char('Name')
    core_id = fields.Many2one('isp.core', string='Core')
    olt_id = fields.Many2one('isp.olt', string='OLT')
    card_id = fields.Many2one('isp.olt.card', string='Card')
    port_id = fields.Many2one('isp.olt.card.port', string='Port')
    radius_id = fields.Many2one('isp.radius', string='Radius')
    is_tr_069 = fields.Boolean('Is TR-069')


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
