# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class IspContract(models.Model):
    _name = 'isp.contract'
    _description = 'Contrato de Servicio ISP'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Campos de Cabecera y Cliente
    name = fields.Char(string="Número de Contrato", required=True, copy=False, readonly=True, default=lambda self: _('Nuevo'))
    partner_id = fields.Many2one('res.partner', string="Cliente", required=True, tracking=True)

    address = fields.Char(string="Dirección de Instalación", required=True)
    phone = fields.Char(string="Teléfono", related='partner_id.phone', readonly=False)

    date_start = fields.Date(string="Fecha de Inicio", default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(string="Fecha de Fin", tracking=True)

    # Campos de Configuración
    payment_type_id = fields.Many2one('isp.payment.type', string="Forma de Pago")
    service_type_id = fields.Many2one('isp.service.type', string="Tipo de Servicio", required=True)
    plan_type_id = fields.Many2one('isp.plan.type', string="Tipo de Plan", required=True)
    contract_term_id = fields.Many2one('isp.contract.term', string="Período de Permanencia")
    cutoff_day_id = fields.Many2one('isp.cutoff.day', string="Día de Corte")
    tag_ids = fields.Many2many('isp.contract.tag', string="Etiquetas")  # TODO: Crear modelo isp.contract.tag

    # Campos de Servicio (reemplazan a los anteriores)
    service_plan_id = fields.Many2one('product.product', string="Plan de Servicio", required=True, domain="[('is_isp_plan', '=', True)]")
    monthly_fee = fields.Float(string="Tarifa Mensual", related='service_plan_id.list_price', readonly=False)


    state = fields.Selection([
        ('draft', 'Borrador'), ('open', 'En Proceso'), ('done', 'Realizado'),
        ('cancel', 'Cancelado'), ('renewal', 'Renovación'),
    ], string="Estado", default='draft', tracking=True)
    state_service = fields.Selection([
        ('inactive', 'Inactivo'), ('active', 'Activo'), ('disabled', 'Cortado'),
        ('suspended', 'Suspendido'), ('removal_list', 'En Lista de Retiro'), ('removed', 'Retirado'),
    ], string="Estado del Servicio", default='inactive', tracking=True)

    # --- Pestaña: Servicios Recurrentes ---
    line_ids = fields.One2many('isp.contract.line', 'contract_id', string='Líneas de Servicio Recurrente', domain=[('line_type', '=', 'recurring')])
    line_debit_ids = fields.One2many('isp.contract.line', 'contract_id', string='Líneas de Cargo Único', domain=[('line_type', '=', 'one_time')])
    payment_type_id = fields.Many2one('isp.payment.type', string="Forma de Pago")
    date_start = fields.Date(string="Fecha de Inicio", default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(string="Fecha de Fin", tracking=True)

    # --- Pestaña: Descuentos/Promociones ---
    discount_plan_id = fields.Many2one('isp.discount.plan', string="Plan de Descuento")
    discount_line_ids = fields.One2many('isp.contract.discount.line', 'contract_id', string='Líneas de Descuento')
    stock_line_ids = fields.One2many('isp.contract.stock.line', 'contract_id', string='Líneas de Materiales')
    payment_promise_ids = fields.One2many('isp.payment.promise', 'contract_id', string="Promesas de Pago")
    anticipated_payment_line_ids = fields.One2many('isp.contract.anticipated.payment.line', 'contract_id', string='Líneas de Pago Anticipado')
    referred_line_ids = fields.One2many('isp.referred.contact', 'contract_id', string='Líneas de Referidos')
    # line_debit_ids = fields.One2many('isp.contract.debit.line', 'contract_id', string='Líneas de Débito/Valores Extra')

    # --- Pestaña: Ubicación ---
    street = fields.Char(string='Calle')
    street2 = fields.Char(string='Calle 2')
    city = fields.Char(string='Ciudad')
    state_id = fields.Many2one('res.country.state', string='Estado/Provincia')
    country_id = fields.Many2one('res.country', string='País')
    zip = fields.Char(string='Código Postal')
    contract_latitude = fields.Float(string='Latitud', digits=(10, 7))
    contract_longitude = fields.Float(string='Longitud', digits=(10, 7))

    # --- Pestaña: Servicio Internet ---
    

    # --- Pestaña: Otra Información ---
    user_id = fields.Many2one('res.users', string='Vendedor', default=lambda self: self.env.user)
    origin = fields.Char(string="Origen Marketing")
    signature = fields.Binary(string="Firma Cliente")
    description_contract = fields.Text(string="Términos y Condiciones")
    holding_id = fields.Many2one('isp.contract.holding', string='Holding/Grupo de Contratos')
    reception_channel_id = fields.Many2one('isp.reception.channel', string='Canal de Recepción')
    tag_ids = fields.Many2many('isp.contract.tag', string="Etiquetas")

    # --- Pestaña: Documentación ---
    doc_vat_copy = fields.Binary(string="Copia de RIF/CI", attachment=True)
    installation_request = fields.Binary(string="Solicitud de Instalación", attachment=True)
    service_contract = fields.Binary(string="Contrato de Servicio Firmado", attachment=True)
    basic_service_sheet = fields.Binary(string="Ficha de Servicio Básico", attachment=True)
    is_validated = fields.Boolean(string="Documentación Validada")

    # --- Pestaña: Notificaciones ---
    is_portal_user = fields.Boolean(string="Es Usuario del Portal", compute="_compute_is_portal_user")
    dont_send_notification_wp = fields.Boolean(string="No Enviar Notificaciones por WhatsApp")
    links_payment = fields.Char(string="Enlaces de Pago", compute="_compute_links_payment", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('isp.contract.sequence') or _('Nuevo')
        return super(IspContract, self).create(vals)

    

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_isp_plan = fields.Boolean(string="Es un Plan ISP", help="Marcar si este producto es un plan de servicio para ISP.")