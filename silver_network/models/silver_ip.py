# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import ipaddress


class SilverIpAddress(models.Model):
    _name = 'silver.ip.address'
    #_table = 'isp_ip_address'
    _description = 'Silver IP Address Range'
    _order = 'name'

    name = fields.Char(string='Description', required=True)
    cidr = fields.Char(string='IP', required=True, help="e.g., 192.168.0.0/24")
#    gateway = fields.Char(string='Gateway')

    core_id = fields.Many2one('silver.core', related='pool_id.core_id', string='Router', store=True)

    pool_id = fields.Many2one('silver.ip.address.pool',  string='Pool')

    public = fields.Boolean(string="Pública", related='pool_id.public')

    is_tr_069 = fields.Boolean(string="Es069")
    used = fields.Boolean(string="Usado", compute='_compute_used', store=True)
    reserved = fields.Boolean(string="Reservado")

    olt_id = fields.Many2one("silver.olt", string="OLT", related="pool_id.olt_id")
    olt_port_id = fields.Many2one("silver.olt.card.port", string="PON", domain="[('olt_id', '=', olt_id)]", related="pool_id.olt_port_id")


    zone_ids = fields.Many2many("silver.zone", string="Zonas", related="pool_id.zone_ids")
    node_ids = fields.Many2many("silver.node", string="Nodos", related="pool_id.node_ids")
    core_ids = fields.Many2many("silver.core", string="Cores", related="pool_id.core_ids")


    #assigned_to = fields.Reference(selection=[], string='Assigned To')
    description = fields.Text()

    _sql_constraints = [
        ('cidr_uniq', 'unique (cidr)', 'Esta ip ya existe!')
    ]


    ip_int = fields.Float(compute='_compute_ip_int', store=True, help="Technical field for sorting")

    @api.depends('name')
    def _compute_ip_int(self):
        for record in self:
            try:
                record.ip_int = int(ipaddress.ip_address(record.name))
            except ValueError:
                record.ip_int = 0

    def _compute_used(self):
        return 0

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [('name', operator, name)]

        print(("ipnamesearch", domain))
        nodes = self.search(domain + args, limit=limit)
        return nodes.name_get()

    @api.model
    def search(self,  domain=None, offset=0, limit=None, order=None):
        ctx = self._context

        if 'order_display' in ctx:
            order = ctx['order_display']
        print(("ipsearch,", order))
        res = super(SilverIpAddress, self).search(
            domain,  offset=offset, limit=limit, order=order)
        return res


class SilverIpAddressLine(models.Model):
    _name = 'silver.ip.address.pool'
    #_table = 'isp_ip_address_pool'
    _description = 'Silver IP Address Line'
    _order = 'public asc, olt_port_id desc, olt_id asc, ip_int asc'

    name = fields.Char(string='Alias', required=False)


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


    address_ids = fields.One2many('silver.ip.address', 'pool_id', string='IPs' )


    is_tr_069 = fields.Boolean(string="Es069")
    public = fields.Boolean(string="Pública")


    ip_int = fields.Integer(compute='_compute_ip_int', store=True, help="Technical field for sorting")

    olt_id = fields.Many2one("silver.olt", string= "OLT")
    olt_port_id = fields.Many2one( "silver.olt.card.port", string= "PON", domain="[('olt_id', '=', olt_id)]")
    core_id = fields.Many2one("silver.core", string="Equipo Router")

    zone_ids = fields.Many2many("silver.zone", string="Zonas")
    node_ids = fields.Many2many("silver.node", string="Nodos")
    core_ids = fields.Many2many("silver.core", string="Cores")


    @api.onchange('network')
    def _onchange_network(self):
        print(("onchangenetwork"))
        if self.network and '/' in self.network:
            try:
                interface = ipaddress.ip_interface(self.network)
                self.network = str(interface.ip)
                self.nmask = interface.network.prefixlen

                print(("nmask", self.nmask, interface))

                if (not self.name) or ipaddress.ip_network(self.name, strict=False):
                    self.name = f"{self.network}/{self.nmask}"

            except ValueError as e:
                print(("error", e))
                # Fail silently on the onchange, the create/write will catch the error
                pass

    def _process_network_field(self, vals):
        if 'network' in vals and vals['network'] and '/' in vals['network']:
            try:
                interface = ipaddress.ip_interface(vals['network'])
                vals['network'] = str(interface.ip)
                vals['nmask'] = interface.network.prefixlen
            except ValueError:
                raise ValidationError(_("El formato de red '%s' no es válido. Use una IP o una notación CIDR como '192.168.1.0/24'.") % vals['network'])
        elif 'network' in vals and vals['network']:
            try:
                # Validate that it's at least a valid IP if no CIDR is present
                ipaddress.ip_address(vals['network'])
            except ValueError:
                raise ValidationError(_("La dirección de red '%s' no es una IP válida.") % vals['network'])
        return vals

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
        vals = self._process_network_field(vals)
        if not vals.get('name'):
            vals['name'] = f"{vals.get('network')}/{vals.get('nmask')}"


        return super(SilverIpAddressLine, self).create(vals)

    def write(self, vals):

        print(("poolwrite", vals))
        vals = self._process_network_field(vals)
        if not 'name' in vals:
            for record in self:
                if not record.name:
                    network = vals.get('network', record.network)
                    nmask = vals.get('nmask', record.nmask)


                    record.name =  f"{network}/{nmask}"
        return super(SilverIpAddressLine, self).write(vals)

    @api.depends('address_ids.used')
    def _compute_usage_stats(self):
        for record in self:
            total = len(record.address_ids)
            used = len(record.address_ids.filtered(lambda r: r.used))
            record.total_ips = total
            record.used_ips = used
            record.usage_percentage = (used / total * 100) if total > 0 else 0.0

    @api.constrains('network', 'nmask')
    def _check_ip_pool_overlap(self):
        for record in self:
            if not record.network or not record.nmask:
                continue
            
            try:
                new_network = ipaddress.ip_network(f"{record.network}/{record.nmask}", strict=False)
            except ValueError:
                continue

            # Buscar otros pools para comparar.
            # Nota: Si hay miles de pools, esto podría optimizarse, pero para configuraciones típicas es rápido.
            domain = [('id', '!=', record.id)]
            other_pools = self.search(domain)
            
            for pool in other_pools:
                if not pool.network or not pool.nmask:
                    continue
                try:
                    existing_network = ipaddress.ip_network(f"{pool.network}/{pool.nmask}", strict=False)
                    if new_network.overlaps(existing_network):
                        raise ValidationError(_(
                            "El rango de red %s se superpone con el pool existente '%s' (%s)."
                        ) % (new_network, pool.name, existing_network))
                except ValueError:
                    continue

    def action_generate_ips(self):
        print(("generate ips"))
        for record in self:
            try:
                network = ipaddress.ip_network(f"{record.network}/{record.nmask}", strict=False)
                print(("network", network))
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

                ip_vals = [{'name': str(ip), 'cidr': str(ip), 'pool_id': record.id,
                            } for ip in network if not  d.get(str(ip))]
                print(("crear ips ", ip_vals, d, dd))
                self.env['silver.ip.address'].create(ip_vals)
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
        ('network_nmask_uniq', 'unique (network, nmask)', 'Ya existe un pool con esta red y máscara.')
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