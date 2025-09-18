from odoo import models, fields, api

class SilverContract(models.Model):
    _name = 'silver.contract'
    _description = 'Contrato de Servicio'
    #_table = 'isp_contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Contrato')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    state = fields.Selection([('draft', 'Borrador'), ('active', 'Activo'), ('cut', 'Cortado'), ('suspended', 'Suspendido')], string='Estado', default='draft')
    start_date = fields.Date(string='Fecha de Inicio')
    end_date = fields.Date(string='Fecha de Fin')
    product_id = fields.Many2one('product.product', string='Plan')
    ip_address = fields.Char(string='Dirección IP')
    mac_address = fields.Char(string='Dirección MAC')
    vlan_id = fields.Many2one('silver.vlan', string='VLAN')
    node_id = fields.Many2one('silver.node', string='Nodo')
    core_id = fields.Many2one('silver.core', string='Equipo Core')
    olt_id = fields.Many2one('silver.olt', string='Equipo OLT')
    olt_card_id = fields.Many2one('silver.olt.card', string='Tarjeta OLT')
    olt_card_port_id = fields.Many2one('silver.olt.card.port', string='Puerto OLT')
    splitter_id = fields.Many2one('silver.splitter', string='Splitter')
    box_id = fields.Many2one('silver.box', string='Caja NAP')
    ap_id = fields.Many2one('silver.ap', string='Equipo AP')
    radius_id = fields.Many2one('silver.radius', string='Servidor Radius')
    onu_id = fields.Many2one('silver.onu.line', string='ONU')
    notes = fields.Text(string='Notas')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
