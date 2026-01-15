from odoo import models, fields, api

class SilverAp(models.Model):
    _name = 'silver.ap'
    #_table = 'isp_ap'
    _description = 'Punto de acceso inalámbrico'

    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char(string="Nombre")


    node_id = fields.Many2one('silver.node', string='Nodo')
    core_id = fields.Many2one('silver.core', 'Equipo Router')
    hostname_ap = fields.Char(string='Hostname')
    node_ids = fields.Many2many('silver.node', string='Nodos', readonly=False)

    #description_brand = fields.Text(string='Descripcion', related='brand_id.description')


    capacity_usage_ap = fields.Integer(string='Usada AP', readonly=False)


   # is_mgn_mac_onu = fields.Boolean(string='Gestion MAC ONU')
    #device_pool_ip_ids = fields.One2many('silver.device.pool.ip', 'ap_id', string='Device Pool Ip')


    ip = fields.Char(string='IP de AP')
    port = fields.Integer(string='Puerto de Conexion')
    username = fields.Char(string='Usuario')
    password = fields.Char(string='Password')
   # type_connection = fields.Selection([("ssh", "SSH"), ("telnet", "Telnet")], string='Tipo de Conexión')
   # port_telnet = fields.Char(string='Puerto telnet', default=23)
   # port_ssh = fields.Char(string='Puerto ssh', default=22)

    # api_hostname = fields.Char(string='Hostname/IP', required=True)
    #api_port = fields.Integer(string='API Port', default=21000, required=True)

    silver_address_id = fields.Many2one('silver.address', string='Dirección')


    latitude = fields.Float(string='Latitud', digits=(10, 7), related='silver_address_id.latitude')
    longitude = fields.Float(string='Longitud', digits=(10, 7), related='silver_address_id.longitude')

   # state = fields.Selection([('down', 'Down'), ('active', 'Active')], string='Estado', default='down')
    state = fields.Selection([('down', 'Down'), ('active', 'Active'), ('connected', 'Connected'),
                      ('connecting', 'Connecting'),
                      ('disconnected', 'Disconnected'),
                      ('error', 'Error')],

                     string='Estado', default='down')

    def action_unlink_from_core(self):
        self.ensure_one()
        self.write({'core_id': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model_create_multi
    def create(self, vals_list):
        print(("createee", vals_list))
        for vals in vals_list:
            if vals.get('core_id'):
                core = self.env['silver.core'].browse(vals['core_id'])
             #   print(("createee0", core, core.name, core.asset_id, core.asset_id.name))
                if core.exists() and core.name:

                #    vals['parent_id'] = core.asset_id.id

                #    vals['name'] = f"{core.name}/{vals.get('hostname_ap', '')}"
                    print(("createe2e", vals))
            print(("createee3", vals))
        return super(SilverAp, self).create(vals_list)


    def write(self, vals):
        print(("apwrite", vals))

        #for record in self:
        #    if vals.get('core_id'):
        #        core = self.env['silver.core'].browse(vals['core_id'])
        #    else:
        #        core = record.core_id

        #    if core.exists() and core.name and 'parent_id' not in vals:
        #        hostname = vals.get('hostname_ap', record.hostname_ap)
        #        record.name = f"{core.name}/{hostname}"
             #   record.parent_id = core.asset_id.id
        #        print(("cocrewr2", hostname))

            # If node_id is set to False, the name is not changed.
        return super(SilverAp, self).write(vals)



    def get_name(self):
        if self.env.context.get('checkboxes'):
            # Sin paréntesis, como solicitaste.
            names = []
            if self.name: names.append(self.name)
            if self.hostname_ap: names.append(self.hostname_ap)
            if self.core_id: names.append(f"{self.core_id}")
            name = " - ".join(names)
        else:
            name = self.name
        return name

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

        records = self.search(domain + args, limit=limit)

        return [(r.id, r.get_name()) for r in records]


    @api.onchange('node_id')
    def _onchange_node_id(self):
        # Primero, verifica si hay un nodo principal anterior para eliminarlo

        previous_nodes_ids = self._origin.node_ids.ids
        print(("previus", previous_nodes_ids))

        # Si había un nodo principal anterior, lo removemos de la lista
        if self._origin.node_id:
            # Creamos un conjunto para una eliminación más eficiente
            nodes_set = set(previous_nodes_ids)
            nodes_set.discard(self._origin.node_id.id)
            current_nodes_ids = list(nodes_set)
        else:
            current_nodes_ids = previous_nodes_ids

        # Ahora, agregamos el ID del nuevo nodo principal si existe
        if self.node_id:
            if self.node_id.id not in current_nodes_ids:
                current_nodes_ids.append(self.node_id.id)

        # Asignar la lista final de IDs al campo many2many usando el comando (6,0,...)
        self.node_ids = [(6, 0, current_nodes_ids)]



        if not self.node_id:
            self.name = ''
            return

        aps = self.env['silver.ap'].search([('node_id', '=', self.node_id.id)])
        i = 1
        for o in aps:
            if o.name:
                patron = r'(\d+)$'
                match = re.search(patron, o.name)
                print(("re", match, i, o))
                if not match: continue
                if (self._origin.id == o.id): continue
                on = int(match.group(1))
                print(("on", on, o.id, self.id, o.id == self.id, self._origin.id == o.id))
                if on >= i: i = on + 1

        name = f"{self.node_id.code}/AP{i}"

        # Construimos el código.
        # Si el campo 'code' del nodo es 'u', y ya tiene 2 cores, el nuevo será 'u/2'
        self.name = name
        print(("h3", self.name))