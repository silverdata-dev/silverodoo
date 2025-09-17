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
    cidr = fields.Char(string='IP', required=True, help="e.g., 192.168.0.0/24")
#    gateway = fields.Char(string='Gateway')
    netdev_id = fields.Many2one('isp.netdev', string='Network Device')

    line_id = fields.Many2one('isp.ip.address.pool',  string='Rango')



    is_tr_069 = fields.Boolean(string="Es069")
    used = fields.Boolean(string="Usado")

    #assigned_to = fields.Reference(selection=[], string='Assigned To')
    description = fields.Text()

    _sql_constraints = [
        ('cidr_uniq', 'unique (cidr)', 'Esta ip ya existe!')
    ]

    status = fields.Selection([
        ('available', 'Available'),
        ('used', 'Used'),
        ('reserved', 'Reserved')
    ], string='Status', default='available', required=True)


class IspIpAddressLine(models.Model):
    _name = 'isp.ip.address.pool'
    _description = 'ISP IP Address Line'
    _order = 'ip_int asc'

    name = fields.Char(string='Alias', required=False)
    #address_id = fields.Many2one('isp.ip.address', string='IP Range', ondelete='cascade', required=True)
    #status = fields.Selection([
    #    ('available', 'Available'),
    #    ('used', 'Used'),
    #    ('reserved', 'Reserved')
    #], string='Status', default='available', required=True)

    assigned_to = fields.Reference(selection=[], string='Assigned To')
    description = fields.Text()

    gateway = fields.Char('Gateway')
    network = fields.Char('Red', required=True)
    broadcast = fields.Char('Broadcast')
    nmask = fields.Integer('Mascara', required=True)
    mask = fields.Char(compute='_computemask', string='Netmask')


    total_ips = fields.Integer(compute='_compute_usage_stats', string='Total IPs')
    used_ips = fields.Integer(compute='_compute_usage_stats', string='Used IPs')
    usage_percentage = fields.Float(compute='_compute_usage_stats', string='Usage (%)', group_operator="avg")


    address_ids = fields.One2many('isp.ip.address', 'line_id', string='IPs' )

    netdev_id = fields.Many2one('isp.netdev', string='Network Device')
    is_tr_069 = fields.Boolean(string="Es069")

    ip_int = fields.Integer(compute='_compute_ip_int', store=True, help="Technical field for sorting")

    def _computemask(self):
        for record in self:

            try:
                # Creamos una interfaz IP ficticia con la máscara dada.
                # No necesitamos una IP real, solo la máscara.
                # Usamos '0.0.0.0' como IP base, ya que solo nos interesa la máscara.
                # O la red: ipaddress.ip_network(f'0.0.0.0/{netmask_cidr}', strict=False)

                # Usamos una IP ficticia y la máscara para obtener el objeto interface
                # y luego su máscara.
                interfaz = ipaddress.ip_interface(f'0.0.0.0/{record.nmask}')

                # La propiedad .netmask nos da el objeto de máscara en notación decimal
                record.mask =  str(interfaz.netmask)

            except ValueError as e:
                print( f"Error: Máscara de subred inválida. {e}")


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



    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = f"{vals.get('network')}/{vals.get('nmask')}"


        return super(IspIpAddressLine, self).create(vals)

    def write(self, vals):
        if not 'name' in vals:
            for record in self:
                if not record.name:
                    network = vals.get('network', record.network)
                    nmask = vals.get('nmask', record.nmask)


                    record.name =  f"{network}/{nmask}"
        return super(IspIpAddressLine, self).write(vals)

    @api.depends('address_ids.status')
    def _compute_usage_stats(self):
        for record in self:
            total = len(record.address_ids)
            used = len(record.address_ids.filtered(lambda r: r.status == 'used'))
            record.total_ips = total
            record.used_ips = used
            record.usage_percentage = (used / total * 100) if total > 0 else 0.0

    def action_generate_ips(self):
        for record in self:
            try:
                network = ipaddress.ip_network(f"{record.network}/{record.nmask}", strict=False)
              #  record.gateway = str(network.network + 1)

                d = {x.cidr:1 for x in record.address_ids}
                dd = {str(ip): 1 for ip in network}

                #if record.address_ids:
                #    raise ValidationError(
                #        _("IPs have already been generated for this range. Please delete them first if you want to regenerate."))

                for a in record.address_ids:
                    if not dd.get(a.cidr):
                        if not a.used:
                            a.unlink()

                ip_vals = [{'name': str(ip), 'cidr': str(ip), 'line_id': record.id, 'netdev_id':record.netdev_id.id} for ip in network if not  d.get(str(ip))]
                print(("crear ips ", ip_vals, d, dd))
                self.env['isp.ip.address'].create(ip_vals)
            except ValueError as e:
                raise ValidationError(_("Invalid CIDR notation: %s") % e)
        return True



    def action_clear_ips(self):
        for record in self:
            try:

                for a in record.address_ids:
                        if not a.used:
                            a.unlink()

            except ValueError as e:
                raise ValidationError(_("Invalid CIDR notation: %s") % e)
        return True

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
    url = fields.Text('Url')

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
