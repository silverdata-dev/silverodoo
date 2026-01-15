from odoo import models, fields, api
import traceback, sys

class SilverOltCardPort(models.Model):
    _name = 'silver.olt.card.port'
    _description = 'Puerto de Tarjeta OLT'
    #_table = 'isp_olt_card_port'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']

    #_inherits = { 'silver.netdev': 'netdev_id'}
    _rec_name = 'name'


    name = fields.Char(string='Nombre')

    #netdev_id = fields.Many2one('silver.netdev', required=True, ondelete="cascade")


    num_port = fields.Integer(string='Numero Puerto')
    olt_id = fields.Many2one('silver.olt', string='Equipo OLT', required=False, ondelete='cascade')
    olt_card_n = fields.Integer(string='Tarjeta', required=False, default=0)
    olt_card_id = fields.Many2one('silver.olt.card', string='Tarjeta OLT', required=False, ondelete='cascade')
    capacity_port_pon = fields.Selection([("32","32"), ("64", "64"), ("128", "128"), ("256","256")], string='Total PON')
    capacity_usage_port_pon = fields.Integer(string='Usada PON', readonly=False)
    #s_vlan = fields.Integer(string='s-vlan')
    #c_vlan = fields.Integer(string='c-vlan')
    #is_management_vlan = fields.Boolean(string='Vlan de Gestion')
    is_extra_serviceport = fields.Boolean(string='Serviport Extra')
    #mgs_vlan = fields.Integer(string='gs-vlan')
    #mgc_vlan = fields.Integer(string='gc-vlan')

    #vlan_ids = fields.Many2many('silver.vlan', 'silver_mvlan_olt_port', 'olt_port_id', 'vlan_id', string='Vlans')
    vlan_ids = fields.One2many('silver.vlan', 'olt_port_id', string='Vlans')

    is_srvprofile = fields.Boolean(string='ONT Srvprofile')
    ont_srvprofile = fields.Char(string='ont-srvprofile')
    is_line_profile = fields.Boolean(string='ONT Lineprofile')
    ont_lineprofile = fields.Char(string='ont-lineprofile')

    #ont_srvprofile_value = fields.Char(string='Valor ont_srvprofile')

    #type_access_net = fields.Selection(
    #    [('inactive', 'Inactivo'), ('dhcp', 'DHCP Leases'), ('manual', 'IP Asignada manualmente'),
    #     ('system', 'IP Asignada por el sistema')], default='inactive', string='Tipo Acceso', required=True, related='netdev_id.type_access_net',)

    dhcp_custom_server = fields.Char(string='DHCP Leases')
    interface = fields.Char(string='Interface')
    dhcp_client = fields.Boolean(string='Profiles VSOL')
    pri_onu_standar = fields.Char(string='PRI ONU Standar:')
    pri_onu_bridge = fields.Char(string='PRI ONU Bridge:')
    is_custom_pppoe_profile = fields.Boolean(string='Custom PPPoE Profile')
    name_custom_pppoe_profile = fields.Char(string='Name Custom PPPoE Profile')
    realm_name = fields.Char(string='REALM')
    is_reverse_onuid = fields.Boolean(string='Reservar ONU IDs')
    number_reverse = fields.Integer(string='Numero')
   # splitter1_count = fields.Integer(string='Conteo Splitter 1', compute='_compute_splitter1_count')
   # splitter2_count = fields.Integer(string='Conteo Splitter 2', compute='_compute_splitter2_count')
   # contracts_port_count = fields.Integer(string='Conteo Puerto Olt', compute='_compute_contracts_port_count')



    ip_address_pool_ids = fields.One2many('silver.ip.address.pool', 'olt_port_id', string='Pools de direcciones IP')
    ip_address_ids = fields.One2many('silver.ip.address', related='ip_address_pool_ids.address_ids', string='Direcciones IP')

    #ip_address_pool_ids = fields.One2many('silver.ip.address.pool', 'olt_port_id', string='Pools de Direcciones IP')
    #ip_address_ids = fields.One2many('silver.ip.address', related='ip_address_pool_ids.address_ids', string='Direcciones IP')

    #    netdev_type = fields.Selection(
    #        related='netdev_id.netdev_type',
    #        default='port',
    #        store=True,
    #        readonly=False
    #    )

    @api.depends('name', 'num_port')
    def _compute_display_name(self):
        for a in self:
            if self.env.context.get('show_n'):
                a.display_name = f"{a.num_port}"
            else:
                a.display_name = f"{a.name}"



    def _compute_splitter1_count(self):
        for record in self:
            record.splitter1_count = self.env['silver.splitter'].search_count([('olt_port_id', '=', record.id), ('type_splitter', '=', '1')])

    def _compute_splitter2_count(self):
        for record in self:
            record.splitter2_count = self.env['silver.splitter'].search_count([('olt_port_id', '=', record.id), ('type_splitter', '=', '2')])


    def create_splitter_primary(self):
        self.ensure_one()
        new_splitter = self.env['silver.splitter'].create({

#            'name': f"Splitter Primary for {self.name}",
#            'olt_port_id': self.id,

            'olt_card_port_id': self.id,
            'type_splitter': '1',
        })
        return {
            'name': 'Splitter Primario Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.splitter',
            'view_mode': 'form',
            'res_id': new_splitter.id,
            'target': 'current',
        }

    def get_name(self):

        return self.name

    @api.model
    def name_create(self, name):


        try:
        #if 1:
            vals = {'name':name}


            card = self.env['silver.olt.card'].search ([('name','=',name.rsplit("/", 1)[0])], limit=1)
            if card and len(card):
                vals['olt_card_id'] = card[0].id
                vals['olt_id'] = card[0].olt_id.id
            else:
                olt = self.env['silver.olt'].search([('name','=',name.rsplit("/", 2)[0])], limit=1)
                if (not olt) or not(len(olt)):
                    oltid,oltname = self.env['silver.olt'].name_create(name.rsplit("/", 2)[0])
                    print(("oltid", oltid, oltname))
                else: oltid = olt[0].id

                vals['olt_id'] = oltid
            if (not card) or (not len(card)):
                cardid,cardname = self.env['silver.olt.card'].name_create(name.rsplit("/", 1)[0])
                card = self.env['silver.olt.card'].browse(cardid)
                print(("cardid", cardid, cardname, card))
                vals['olt_card_id'] = card.id
                vals['olt_id'] = card.olt_id.id

            print("createport",vals, card, len(card))
            r= self.create(vals)
            print("created ", r)


            self.env.flush_all()


        #    return r.name_get()[0]
        except Exception as e:
            print(("perror", e))
            traceback.print_exc(file=sys.stdout)

#        print(("create slot", name, self.env.context, r))

        return r.id, r.name


    def name_get(self):
        """
        Método estándar de Odoo para obtener el nombre a mostrar.
        Aquí manejamos el contexto para mostrar las coordenadas.
        """
        result = []
        for rec in self:

            name = self.get_name()


            # Si no hay datos de dirección legible, usamos el display_name
            if not name:
                name = rec.display_name
            result.append((rec.id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Permite buscar direcciones por calle, edificio o nombre de la zona.
        """

        args = args or []
        domain = []
        try:
            if name:

                    domain = [('name', operator, name)]

            records = self.search(domain + args, limit=limit)
            #ps = self.search([], limit=1)
            #nps = [p.name for p in ps]

            if len(records)!=1:
                print(("psearchname", records, name, args, operator))

            return [(r.id, r.get_name()) for r in records]
        except Exception as e:
            print(("peerroorr",e))
            return []


    def create_splitter_secondary(self):
        self.ensure_one()
        new_splitter = self.env['silver.splitter'].create({

#            'name': f"Splitter Secondary for {self.name}",
#            'olt_port_id': self.id,

            'olt_card_port_id': self.id,
            'type_splitter': '2',
        })
        return {
            'name': 'Splitter Secundario Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.splitter',
            'view_mode': 'form',
            'res_id': new_splitter.id,
            'target': 'current',
        }

    def action_view_splitter1(self):
        self.ensure_one()
        return {
            'name': 'Splitter Primario',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.splitter',
            'view_mode': 'list,form',
            'domain': [('olt_card_port_id', '=', self.id), ('type_splitter', '=', '1')],
            'context': {'default_olt_card_port_id': self.id, 'default_type_splitter': '1'},
            'target': 'current',
        }

    def action_view_splitter2(self):
        self.ensure_one()
        return {
            'name': 'Splitter Secundario',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.splitter',
            'view_mode': 'list,form',
            'domain': [('olt_card_port_id', '=', self.id), ('type_splitter', '=', '2')],
            'context': {'default_olt_card_port_id': self.id, 'default_type_splitter': '2'},
            'target': 'current',
        }


    def generar(self):
        for record in self:
            for ret in record.ip_address_pool_ids:
                print(("ret", ret))
                ret.action_generate_ips()
