# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import math

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos geográficos
    utilizando la fórmula de Haversine.
    """
    R = 6371  # Radio de la Tierra en kilómetros
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

class SilverContract(models.Model):
    _name = 'silver.contract'
    _description = 'Contrato de Servicio ISP'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    image = fields.Binary(string='Cédula')
    # Campos de Cabecera y Cliente
    name = fields.Char(string="Número de Contrato", required=True, copy=False, readonly=True, default=lambda self: _('Nuevo'))
    partner_id = fields.Many2one('res.partner', string="Cliente", required=True, tracking=True)

    address = fields.Char(string="Dirección de Instalación", required=True)
    phone = fields.Char(string="Teléfono", related='partner_id.phone', readonly=False)

    date_start = fields.Date(string="Fecha de Inicio", default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(string="Fecha de Fin", tracking=True)

    # Campos de Configuración
   # payment_type_id = fields.Many2one('silver.payment.type', string="Forma de Pago")
    service_type_id = fields.Many2one('silver.service.type', string="Tipo de Servicio", required=True)
    plan_type_id = fields.Many2one('silver.plan.type', string="Tipo de Plan", required=True)
    contract_term_id = fields.Many2one('silver.contract.term', string="Período de Permanencia")
    cutoff_date_id = fields.Many2one('silver.cutoff.date', string="Periodo de Consumo")
    tag_ids = fields.Many2many('silver.contract.tag', string="Etiquetas")  # TODO: Crear modelo silver.contract.tag

    # Campos de Servicio (reemplazan a los anteriores)
 #   service_plan_id = fields.Many2one('product.product', string="Plan de Servicio", required=True, domain="[('is_silver_plan', '=', True)]")
 #   monthly_fee = fields.Float(string="Tarifa Mensual", related='service_plan_id.list_price', readonly=False)


    state = fields.Selection([
        ('draft', 'Borrador'), ('open', 'En Proceso'), ('done', 'Realizado'),
        ('cancel', 'Cancelado'), ('renewal', 'Renovación'),
    ], string="Estado", default='draft', tracking=True)
    state_service = fields.Selection([
        ('inactive', 'Inactivo'), ('active', 'Activo'), ('disabled', 'Cortado'),
        ('suspended', 'Suspendido'), ('removal_list', 'En Lista de Retiro'), ('removed', 'Retirado'),
    ], string="Estado del Servicio", default='inactive', tracking=True)

    # --- Pestaña: Servicios Recurrentes ---
    recurring_invoice_type = fields.Selection([('post', 'Postpago'), ('pre', 'Prepago')], string="Tipo de Consumo")
    recurring_invoicing_type = fields.Selection([('recurrent', 'Recurrente'), ('one_time', 'Una sola vez')], string="Tipo de facturación")
    line_ids = fields.One2many('silver.contract.line', 'contract_id', string='Líneas de Servicio Recurrente', domain=[('line_type', '=', 'recurring')])
    line_debit_ids = fields.One2many('silver.contract.line', 'contract_id', string='Líneas de Cargo Único', domain=[('line_type', '=', 'one_time')])
    payment_type_id = fields.Many2one('silver.payment.type', string="Forma de Pago")
  #  date_start = fields.Date(string="Fecha de Inicio", default=fields.Date.context_today, tracking=True)
   # date_end = fields.Date(string="Fecha de Fin", tracking=True)
    type_journal_invoice = fields.Selection([('invoice', 'Factura'), ('receipt','Nota de entrega/Recibo' )], 'Tipo de Documento')
    recurring_invoices = fields.Boolean(string='Recurrencia')
    is_recurring_invoicing_type = fields.Boolean(string="ES tipo de facturacion")
    recurring_next_date = fields.Date(string="Fecha próxima factura")
    recurring_interval = fields.Integer(string="Facturar Cada")
    recurring_rule_type = fields.Selection([('daily', 'Días'), ('weekly', 'Semanas'), ('monthly', 'Meses'), ('yearly', 'Años')], string="Regla")
    is_select_journal_invoice = fields.Boolean(string="¿Escoger diario de Factura?")
    is_first_invoice = fields.Boolean(string="Primera Factura Generada")
    is_extra_value = fields.Boolean(string="¿Ya facturo valores extra?")
    is_extra_value_active = fields.Boolean(string="¿Esta activo facturar valores extra?")
    payment_type_code = fields.Char(related='payment_type_id.code')
    # --- Pestaña: Descuentos/Promociones ---
    discount_plan_id = fields.Many2one('silver.discount.plan', string="Plan de Descuento")
    discount_line_ids = fields.One2many('silver.contract.discount.line', 'contract_id', string='Líneas de Descuento')
    contract_discount_id = fields.Many2one('silver.discount.plan', string="Promoción")
    active_payment_anticipated = fields.Boolean(string="Activar Pago Anticipado")
    contract_discount_ids = fields.Many2many('silver.discount.plan', string="Descuentos Permitidos")
    promotion_active = fields.Boolean(string="Promoción Activa")
    contract_discount_line_id = fields.Many2one('silver.contract.discount.line', string="Línea de Promoción")
    is_disabled = fields.Boolean(string="Es Discapacitado?")
    disability_percentage = fields.Float(string="Porcentaje de Discapacidad")
    is_senior = fields.Boolean(string="Tercera Edad?")
    has_promotion_foreign_currency = fields.Boolean(string="Tiene Promoción Pago en Divisa")
    #foreign_currency_line_ids = fields.One2many('foreign.currency.line', 'contract_id', string="Lineas de Descuento")
    stock_line_ids = fields.One2many('silver.contract.stock.line', 'contract_id', string='Líneas de Materiales')
    payment_promise_ids = fields.One2many('silver.payment.promise', 'contract_id', string="Promesas de Pago")
    anticipated_payment_line_ids = fields.One2many('silver.contract.anticipated.payment.line', 'contract_id', string='Líneas de Pago Anticipado')
    referred_line_ids = fields.One2many('silver.referred.contact', 'contract_id', string='Líneas de Referidos')
    # line_debit_ids = fields.One2many('silver.contract.debit.line', 'contract_id', string='Líneas de Débito/Valores Extra')
 
    # --- Pestaña: Ubicación ---
    street = fields.Char(string='Calle')
    street2 = fields.Char(string='Calle 2')
    city = fields.Char(string='Ciudad')
    state_id = fields.Many2one('res.country.state', string='Estado/Provincia')
    country_id = fields.Many2one('res.country', string='País', default=lambda self: self._get_default_country())
    zip = fields.Char(string='Código Postal')
    contract_latitude = fields.Float(string='Latitud', digits=(10, 7))
    contract_longitude = fields.Float(string='Longitud', digits=(10, 7))

    onuid = fields.Integer(string="ONU-id")




    # --- Pestaña: Otra Información ---
    user_id = fields.Many2one('res.users', string='Vendedor', default=lambda self: self.env.user)
    origin = fields.Char(string="Origen Marketing")
    signature = fields.Binary(string="Firma Cliente")
    description_contract = fields.Text(string="Términos y Condiciones")
    holding_id = fields.Many2one('silver.contract.holding', string='Holding/Grupo de Contratos')
    reception_channel_id = fields.Many2one('silver.reception.channel', string='Canal de Recepción')
    is_other_partner_bank = fields.Boolean(string="Diferente propietario de cuenta?")
    partner_bank_id = fields.Many2one('res.partner', string="Propietario cuenta")
    res_partner_bank_id = fields.Many2one('res.partner.bank', string="Cuenta bancaria")

  #  payment_type_code = fields.Char(string="Código forma de pago")


    # --- Pestaña: Documentación ---
    doc_vat_copy = fields.Binary(string="Copia de RIF/CI", attachment=True)
    doc_vat_copy_filename = fields.Char(string="Nombre de archivo de Copia de RIF/CI")
    installation_request = fields.Binary(string="Solicitud de Instalación", attachment=True)
    installation_request_filename = fields.Char(string="Nombre de archivo de Solicitud de Instalación")
    service_contract = fields.Binary(string="Contrato de Servicio Firmado", attachment=True)
    service_contract_filename = fields.Char(string="Nombre de archivo de Contrato de Servicio Firmado")
    basic_service_sheet = fields.Binary(string="Ficha de Servicio Básico", attachment=True)
    basic_service_sheet_filename = fields.Char(string="Nombre de archivo de Ficha de Servicio Básico")
    is_validated = fields.Boolean(string="Documentación Validada")

    # --- Pestaña: Notificaciones ---
    is_portal_user = fields.Boolean(string="Es Usuario del Portal", compute="_compute_is_portal_user")
    dont_send_notification_wp = fields.Boolean(string="No Enviar Notificaciones por WhatsApp")
    links_payment = fields.Char(string="Enlaces de Pago", compute="_compute_links_payment", readonly=True)

    @api.onchange('contract_latitude', 'contract_longitude')
    def _onchange_coordinates(self):
        if self.contract_latitude and self.contract_longitude:
            # Encuentra el nodo más cercano
            nodes = self.env['isp.node'].search([])
            closest_node = None
            min_dist_node = float('inf')
            for node in nodes:
                if node.latitude and node.longitude:
                    dist = haversine(self.contract_latitude, self.contract_longitude, node.latitude, node.longitude)
                    if dist < min_dist_node:
                        min_dist_node = dist
                        closest_node = node
            self.node_id = closest_node

            # Encuentra la caja NAP más cercana
            boxes = self.env['isp.box'].search([])
            closest_box = None
            min_dist_box = float('inf')
            for box in boxes:
                if box.latitude and box.longitude:
                    dist = haversine(self.contract_latitude, self.contract_longitude, box.latitude, box.longitude)
                    if dist < min_dist_box:
                        min_dist_box = dist
                        closest_box = box
            self.box_id = closest_box

    @api.onchange('box_id')
    def _onchange_box_id(self):
        if self.box_id:
            self.core_id = self.box_id.core_id
            self.olt_id = self.box_id.olt_id
        else:
            self.core_id = False
            self.olt_id = False

    def _get_default_country(self):
        return self.env['res.country'].search([('code', '=', 'VE')], limit=1)

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('silver.contract.sequence') or _('Nuevo')
        return super(SilverContract, self).create(vals)

    def action_open(self):
        return None


    def action_cancel(self):
        return None


    def action_register_notification(self):
        pass

    def action_amountdue_notification(self):
        pass

    def enable_portal_access_contract(self):
        pass

    def action_cutoff_notification(self):
        pass

    def disable_portal_access_contract(self):
        pass

    def action_generate_first_invoice(self):
        pass

    def action_generate_first_ext_materials(self):
        pass

    def action_assing_discount(self):
        pass

    def action_assing_discount_manual(self):
        pass


    def _compute_is_portal_user(self):
        for rec in self:
            rec.is_portal_user = False

    def _compute_links_payment(self):
        for rec in self:
            rec.links_payment = ''
