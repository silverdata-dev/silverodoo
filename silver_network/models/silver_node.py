
from datetime import datetime
from odoo import models, fields, api

class SilverNode(models.Model):
    _name = 'silver.node'
    _description = 'Nodo ISP'
    #_table = 'isp_node'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _inherits = {'silver.asset': 'asset_id'}

    asset_id = fields.Many2one('silver.asset', required=True, ondelete="cascade")

    code = fields.Char(string="Codigo interno", related='asset_id.code', required=True, readonly=False)

#    _sql_constraints = [
#        ('unique_code', 'unique (code)', 'This value must be unique!')
#    ]

    phone = fields.Char(string='Teléfono')

    distance = fields.Float(string='Distancia')

    journal_id = fields.Many2one('account.journal', string='Diario')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica de Ingresos')
    account_cost_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica de Costos')

    core_count = fields.Integer(string='Equipos Core', compute='_compute_counts')
  #aa  support_ticket_count = fields.Integer(string='Tickets', compute='_compute_counts')
  #aa  stock_picking_count = fields.Integer(string='Movimientos', compute='_compute_counts')
    olt_count = fields.Integer(string='Equipos OLT', compute='_compute_counts')

    core_ids = fields.One2many('silver.core', 'node_id', string='Cores')
    olt_ids = fields.One2many('silver.olt', 'node_id', string='OLTs')
    box_ids = fields.One2many('silver.box', 'node_id', string='Boxes')
    #splice_closure_ids = fields.One2many('silver.splice_closure', 'node_id', string='Splice Closures')


    silver_address_id = fields.Many2one('silver.address', string='Dirección')



    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='node',
        store=True,
        readonly=False
    )


   # @api.model
   # def create(self, vals):
   #     if vals.get('gps_lon') and vals.get('gps_lat'):
   #         vals['date_localization'] =  datetime.now()
   #     return super(SilverNode, self).create(vals)

   # @api.model
   # def write(self, vals):
   #     if vals.get('gps_lon') and vals.get('gps_lat'):
   #         vals['date_localization'] = datetime.now()

   #     for record in self:
   #         if (vals.get('gps_lon') or vals.get('gps_lat')):
   #             record.date_localization =  datetime.now()
   #             print(("record", record, record.date_localization))
   #     return super(SilverNode, self).write(vals)


    def _compute_counts(self):
        for record in self:
            record.core_count = self.env['silver.core'].search_count([('node_id', '=', record.id)])
            # Assuming 'helpdesk.ticket' has a 'node_id' field.
         #aa   record.support_ticket_count = self.env['helpdesk.ticket'].search_count([('node_id', '=', record.id)])
            # Assuming 'stock.picking' can be related to a node.
            # This might need adjustment depending on the actual data model.
            # For now, I'll assume a many2one field 'node_id' exists on stock.picking for demonstration.
         #aa   record.stock_picking_count = self.env['stock.picking'].search_count([('node_id', '=', record.id)])
            record.olt_count = self.env['silver.olt'].search_count([('node_id', '=', record.id)])

    def create_core(self):
        self.ensure_one()
        new_core = self.env['silver.core'].create({
            #'name': f"Core for {self.name}",
            'node_id': self.id,
        })

        return {
            'name': 'Core Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.core',
            'view_mode': 'form',
            'res_id': new_core.id,
            'target': 'current',
        }

    def action_create_ticket_node(self):
        self.ensure_one()
        # Asumiendo que el modelo helpdesk.ticket existe y tiene un campo 'name' y 'node_id'
        new_ticket = self.env['helpdesk.ticket'].create({
            'name': f"Ticket for {self.name}",
            'node_id': self.id,
        })
        return {
            'name': 'Ticket Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'form',
            'res_id': new_ticket.id,
            'target': 'current',
        }

    def create_olt(self):
        """
        Crea un nuevo registro de OLT y lo asocia con el nodo actual.
        """
        self.ensure_one()  # Asegura que el método se ejecute en un único registro

        # Crea el nuevo registro silver.olt
        new_olt = self.env['silver.olt'].create({
#            'name': f"OLT for {self.name}",
            'node_id': self.id,

            # Puedes añadir más campos aquí, como 'serial_number', 'model', etc.
        })

        # Opcionalmente, puedes devolver una acción de ventana para abrir el formulario del OLT recién creado
        return {
            'name': 'OLT Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.olt',
            'view_mode': 'form',
            'res_id': new_olt.id,
            'target': 'current',
        }


    def action_search_view_olts(self):
        self.ensure_one()
        return {
            'name': 'OLTs',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.olt',
            'view_mode': 'tree,form',
            'domain': [('node_id', '=', self.id)],
            'target': 'current',
        }

    def action_view_cores(self):
        self.ensure_one()
        return {
            'name': 'Cores',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.core',
            'view_mode': 'tree,form',
            'domain': [('node_id', '=', self.id)],
            'context': {'default_node_id': self.id},
            'target': 'current',
        }

    def action_view_support_tickets(self):
        self.ensure_one()
        return {
            'name': 'Tickets',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'tree,form',
            'domain': [('node_id', '=', self.id)],
            'context': {'default_node_id': self.id},
            'target': 'current',
        }

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        nodes = self.search(domain + args, limit=limit)
        return nodes.name_get()

