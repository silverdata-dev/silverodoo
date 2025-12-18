# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import math
from odoo.exceptions import UserError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import logging

_logger = logging.getLogger(__name__)

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
    phone = fields.Char(string="Teléfono", related='partner_id.phone', readonly=False)

    date_start = fields.Date(string="Fecha de Inicio", default=fields.Date.context_today, tracking=True, readonly=True, states={'draft': [('readonly', False)], 'open': [('readonly', False)]})
    date_end = fields.Date(string="Fecha de Fin", tracking=True, readonly=True)



    # Campos de Configuración
    service_type_id = fields.Many2one('silver.service.type', string="Tipo de Servicio", required=True, default=lambda self: self._get_default_service_type_id())
    service_type_code = fields.Char(related='service_type_id.code', string="Código de Tipo de Servicio", store=False)
    plan_type_id = fields.Many2one('silver.plan.type', string="Tipo de Plan", required=True, default=lambda self: self._get_default_plan_type_id())
    payment_type_id = fields.Many2one('silver.payment.type', string="Forma de Pago",  default=lambda self: self._get_default_payment_type_id())

    contract_term_id = fields.Many2one('silver.contract.term', string="Período de Permanencia",  default=lambda self: self._get_default_contract_term_id())
    cutoff_date_id = fields.Many2one('silver.cutoff.date', string="Periodo de Consumo")
    tag_ids = fields.Many2many('silver.contract.tag', string="Etiquetas")

    state = fields.Selection([
        ('draft', 'Borrador'),('open', 'Abierto'), ('active', 'Activo'),('closed', 'Cerrado')
    ], string="Estado del Contrato", default='draft', tracking=True)

    state_service = fields.Selection([
        ('inactive', 'Inactivo'), ('active', 'Activo'),
        ('suspended', 'Suspendido'), ('terminated', 'De Baja'),
    ], string="Estado del Servicio", default='inactive', tracking=True)

    # --- Pestaña: Ubicación (NUEVO) ---
    silver_address_id = fields.Many2one('silver.address', string='Dirección de Instalación')
    #box_id = fields.Many2one('silver.box', string='Caja NAP')

    # --- Pestaña: Servicios Recurrentes ---
    #recurring_invoice_type = fields.Selection([('post', 'Postpago'), ('pre', 'Prepago')], string="Tipo de Consumo")
    #recurring_invoicing_type = fields.Selection([('recurrent', 'Recurrente'), ('one_time', 'Una sola vez')], string="Tipo de facturación")
    recurring_invoicing_type = fields.Selection([('post', 'Postpago'), ('pre', 'Prepago')],
                                                string="Tipo de facturación", default='pre')
    line_ids = fields.One2many('silver.contract.line', 'contract_id', string='Líneas de Servicio Recurrente', domain=[('line_type', '=', 'recurring')])
    line_debit_ids = fields.One2many('silver.contract.line', 'contract_id', string='Líneas de Cargo Único', domain=[('line_type', '=', 'one_time')])
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

    line_id = fields.Many2one('silver.contract.line',compute="computeline", # Si viene de un O2M
        store=True,
        readonly=True
    )
    
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
    payment_promise_ids = fields.One2many('silver.payment.promise', 'contract_id', string="Promesas de Pago")
    anticipated_payment_line_ids = fields.One2many('silver.contract.anticipated.payment.line', 'contract_id', string='Líneas de Pago Anticipado')
    referred_line_ids = fields.One2many('silver.referred.contact', 'contract_id', string='Líneas de Referidos')

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

    @api.depends('line_ids')
    def computeline(self):
        self.line_id = self.line_ids[0] if self.line_ids else None

    @api.onchange('partner_id')
    def _onchange_partner_id_silver(self):
        # Este onchange podría ser problemático si un cliente tiene múltiples contratos
        # y se quiere que cada uno tenga una dirección de instalación diferente.
        # Por ahora, lo mantenemos pero con un comentario de advertencia.
        if self.partner_id and self.partner_id.silver_address_id:
            original_address = self.partner_id.silver_address_id

            # Prepara los datos para la copia
            address_data = original_address.copy_data({
                'parent_id': original_address.id,
            })[0]

            # Crea la nueva dirección (la copia)
            new_address = self.env['silver.address'].create(address_data)

            # Asigna la nueva dirección al contrato
            self.silver_address_id = new_address
        else:
            self.silver_address_id = False




    @api.onchange('silver_address_id')
    def _onchange_silver_address_id(self):
        if self.silver_address_id and self.silver_address_id.latitude and self.silver_address_id.longitude:
            addr_lat = self.silver_address_id.latitude
            addr_lon = self.silver_address_id.longitude

            closest_box = self.env['silver.box'].search([
                ('asset_type', '=', 'nap'),
                ('latitude', '!=', 0),
                ('longitude', '!=', 0)
            ]).sorted(key=lambda b: (b.latitude - addr_lat)**2 + (b.longitude - addr_lon)**2)

       #     if closest_box:
       #         self.box_id = closest_box[0]
       #     else:
       #         self.box_id = False
       ## else:
        #    self.box_id = False

    def _get_default_country(self):
        return self.env['res.country'].search([('code', '=', 'VE')], limit=1)


    def _get_default_plan_type_id(self):
        return self.env['silver.plan.type'].search([('code', '=', 'residencial')], limit=1)

    def _get_default_service_type_id(self):
        return self.env['silver.service.type'].search([('code', '=', 'internet')], limit=1)

    def _get_default_payment_type_id(self):
        return self.env['silver.payment.type'].search([('code', '=', 'cash')], limit=1)

    def _get_default_contract_term_id(self):
        return self.env['silver.contract.term'].search([('name', '=', '12')], limit=1)

    @api.model
    def create(self, vals):
        #if (vals.get('name') in [None, 'Nuevo']):
        #    vals['name'] = self.env['ir.sequence'].next_by_code('silver.contract.sequence')
        print(("creae0", vals))
        return super(SilverContract, self).create(vals)



    def init_contract(self):
        for a in self:
            if not a.line_ids:
                raise UserError(_("Debe haber al menos un servicio"))

            a.name = self.env['ir.sequence'].next_by_code('silver.contract.sequence')
            a.state = 'open'

            a.pppoe_user = a.name.split('-')[-1]
        return True


    def close_contract(self):
        for a in self:
            a.state = 'closed'

        return True

    def _calculate_next_recurring_invoice_date(self, current_date):
        """
        Calcula la próxima fecha de facturación recurrente basándose en la política de corte.
        :param current_date: La fecha actual o la fecha de la última factura.
        :return: La próxima fecha de facturación (date).
        """
        self.ensure_one()
        policy = self.cutoff_date_id
        if not policy:
            return False

        next_date = False

        if policy.type_cut == 'days':
            # Corte por día fijo del mes
            cutoff_day = policy.day_cut
            # Intentar el día de corte en el mes actual
            try:
                next_date = current_date.replace(day=cutoff_day)
            except ValueError:
                # Si el día de corte es mayor que los días del mes (ej. 31 en Febrero), usar el último día del mes
                last_day_of_month = calendar.monthrange(current_date.year, current_date.month)[1]
                next_date = current_date.replace(day=last_day_of_month)
            
            # Si la fecha calculada es igual o anterior a la fecha actual, avanzar al siguiente mes
            if next_date <= current_date:
                next_date += relativedelta(months=1)
                try:
                    next_date = next_date.replace(day=cutoff_day)
                except ValueError:
                    last_day_of_month = calendar.monthrange(next_date.year, next_date.month)[1]
                    next_date = next_date.replace(day=last_day_of_month)

        elif policy.type_cut == 'date':
            # Corte basado en el día de inicio del contrato (mensual)
            # Asumimos que el ciclo es mensual si type_cut es 'date'
            next_date = current_date + relativedelta(months=1)
            # Asegurarse de que el día del mes sea el mismo que el de inicio del contrato
            # Manejar el caso de fin de mes (ej. 31 de enero -> 28 de febrero)
            try:
                next_date = next_date.replace(day=self.date_start.day)
            except ValueError:
                last_day_of_month = calendar.monthrange(next_date.year, next_date.month)[1]
                next_date = next_date.replace(day=last_day_of_month)

        return next_date


    def _calculate_first_invoice_date_and_proration(self):
        """
        Calcula la fecha de la primera factura y el prorrateo si aplica.
        Esta función se llama desde start_contract.
        """
        self.ensure_one()
        policy = self.cutoff_date_id
        if not policy:
            return

        activation_date = self.date_start
        next_invoice_date = False

        # --- 1. Calcular la fecha de la próxima factura ---
        # Reutilizamos la lógica de _calculate_next_recurring_invoice_date
        # pero con la consideración de que es la primera vez.
        # La primera fecha de facturación es la primera fecha de corte *después* de la activación.
        
        # Calcular la primera fecha de corte posible
        if policy.type_cut == 'days':
            cutoff_day = policy.day_cut
            try:
                first_possible_cutoff = activation_date.replace(day=cutoff_day)
            except ValueError:
                last_day_of_month = calendar.monthrange(activation_date.year, activation_date.month)[1]
                first_possible_cutoff = activation_date.replace(day=last_day_of_month)
            
            if first_possible_cutoff < activation_date:
                # Si el día de corte ya pasó en el mes de activación, la primera factura es el próximo mes
                first_possible_cutoff += relativedelta(months=1)
                try:
                    first_possible_cutoff = first_possible_cutoff.replace(day=cutoff_day)
                except ValueError:
                    last_day_of_month = calendar.monthrange(first_possible_cutoff.year, first_possible_cutoff.month)[1]
                    first_possible_cutoff = first_possible_cutoff.replace(day=last_day_of_month)
            next_invoice_date = first_possible_cutoff

        elif policy.type_cut == 'date':
            # El corte es basado en el día de inicio del contrato
            # La primera factura será un mes después de la activación, manteniendo el día de activación
            next_invoice_date = activation_date + relativedelta(months=1)
            # Asegurarse de que el día del mes sea el mismo que el de inicio del contrato
            try:
                next_invoice_date = next_invoice_date.replace(day=activation_date.day)
            except ValueError:
                last_day_of_month = calendar.monthrange(next_invoice_date.year, next_invoice_date.month)[1]
                next_invoice_date = next_invoice_date.replace(day=last_day_of_month)

        if not next_invoice_date:
            _logger.warning(f"No se pudo calcular la próxima fecha de factura para el contrato {self.name}")
            return

        self.recurring_next_date = next_invoice_date

        # --- 2. Calcular y crear el cargo de prorrateo ---
        # Solo prorratear si la política lo permite y si la activación no es en el día de corte
        if policy.is_apportion and activation_date != next_invoice_date:
            total_monthly_price = sum(self.line_ids.mapped('price_unit'))
            if total_monthly_price <= 0:
                return

            # Días en el mes de activación (o el mes que abarca el prorrateo)
            # Consideramos el periodo desde la activación hasta la primera fecha de factura
            delta_days = (next_invoice_date - activation_date).days
            
            if delta_days <= 0: # No hay días para prorratear o ya se facturó
                return

            # Calcular la tarifa diaria basada en el mes de activación
            days_in_month_of_activation = calendar.monthrange(activation_date.year, activation_date.month)[1]
            daily_rate = total_monthly_price / days_in_month_of_activation

            proration_amount = daily_rate * delta_days

            if proration_amount > 0:
                # Buscar un producto genérico para prorrateo o usar el del primer servicio
                product_proration = self.env['product.product'].search([('name', '=', 'Prorrateo Servicio')], limit=1)
                if not product_proration and self.line_ids:
                    product_proration = self.line_ids[0].product_id
                
                if product_proration:
                    self.env['silver.contract.line'].create({
                        'contract_id': self.id,
                        'name': _('Prorrateo por activación (%s días)') % delta_days,
                        'price_unit': proration_amount,
                        'line_type': 'one_time',
                        'product_id': product_proration.id,
                        'invoiced': False, # Asegurarse de que no esté facturado aún
                    })
                else:
                    _logger.warning(f"No se encontró producto para prorrateo en contrato {self.name}")

    def start_contract(self):
        """
        Activa el contrato, calcula la fecha de la primera factura y el prorrateo.
        """
        for contract in self:
            if contract.state not in ['draft', 'open']:
                continue
            
            contract.state = 'active'
            contract.state_service = 'active'
            contract._calculate_first_invoice_date_and_proration()

        return True

    @api.model
    def _cron_generate_invoices(self):
        """
        Cron Job para generar facturas recurrentes de contratos activos.
        """
        _logger.info("Iniciando Cron Job: Generación de Facturas Recurrentes")
        today = fields.Date.today()

        contracts_to_invoice = self.search([
            ('state', '=', 'active'),
            ('recurring_next_date', '<=', today),
            ('cutoff_date_id', '!=', False), # Asegurarse de que tenga una política de corte
        ])

        print(("cron inv", contracts_to_invoice))

        for contract in contracts_to_invoice:
            _logger.info(f"Generando factura para contrato {contract.name} (ID: {contract.id})...")
            invoice_lines_vals = []
            lines_to_mark_invoiced = self.env['silver.contract.line'] # Para marcar como facturadas

            # 1. Añadir líneas de servicio recurrentes
            for line in contract.line_ids.filtered(lambda l: l.line_type == 'recurring'):
                invoice_lines_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'currency_id': line.currency_id.id,
                }))

            # 2. Añadir líneas de cargo único (incluyendo prorrateos) que no han sido facturadas
            for line in contract.line_debit_ids.filtered(lambda l: not l.invoiced):
                invoice_lines_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'currency_id': line.currency_id.id,
                }))
                lines_to_mark_invoiced += line # Añadir a la lista para marcar después

            if not invoice_lines_vals:
                _logger.warning(f"Contrato {contract.name} (ID: {contract.id}) no tiene líneas para facturar. Saltando.")
                continue

            try:
                # Crear la factura
                invoice = self.env['account.move'].create({
                    'partner_id': contract.partner_id.id,
                    'move_type': 'out_invoice',
                    'contract_id': contract.id, # Enlazar la factura al contrato
                    'invoice_date': today,
                    'invoice_line_ids': invoice_lines_vals,
                })
                invoice.action_post() # Validar la factura

                # Marcar las líneas de cargo único como facturadas
                lines_to_mark_invoiced.write({'invoiced': True})

                # Actualizar la próxima fecha de facturación del contrato
                new_next_invoice_date = contract._calculate_next_recurring_invoice_date(contract.recurring_next_date)
                contract.write({'recurring_next_date': new_next_invoice_date})
                _logger.info(f"Factura {invoice.name} generada y validada para contrato {contract.name}. Próxima fecha: {new_next_invoice_date}")

            except Exception as e:
                _logger.error(f"Error al generar factura para contrato {contract.name} (ID: {contract.id}): {e}")
                self.env.cr.rollback() # Revertir la transacción para este contrato en caso de error
                continue # Continuar con el siguiente contrato

        _logger.info("Cron Job: Generación de Facturas Recurrentes finalizado.")


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

    @api.model
    def _cron_auto_suspend_reactivate_contracts(self):
        """
        Tarea programada para suspender servicios de contratos con pagos atrasados
        y reactivar servicios de contratos con pagos al día.
        """
        _logger.info("Iniciando Cron Job: Corte y Reconexión Automática de Contratos")
        today = fields.Date.today()

        # --- Lógica de Suspensión ---
        # Buscar contratos activos que deberían estar suspendidos (lógica de deuda pendiente)
        contracts_to_suspend = self.search([
            ('state_service', '=', 'active'),
            # GEMINI: Aquí se añadiría la lógica para determinar si un contrato tiene deuda pendiente
            # Por ejemplo, basándose en facturas no pagadas o fecha de corte excedida.
            # Por ahora, solo es un placeholder.
            # ('has_overdue_invoices', '=', True)
        ])
        
        for contract in contracts_to_suspend:
            _logger.info(f"Suspendiendo servicio para contrato {contract.name}...")
            # GEMINI: Llamar a la función de suspensión de servicio en silver_provisioning
            # contract.action_suspend_service() # Esta función debe ser implementada
            contract.write({'state_service': 'suspended'}) # Placeholder

        # --- Lógica de Reactivación ---
        # Buscar contratos suspendidos que deberían estar activos (pagos al día)
        contracts_to_reactivate = self.search([
            ('state_service', '=', 'suspended'),
            # GEMINI: Aquí se añadiría la lógica para determinar si un contrato ya pagó su deuda
            # ('has_no_overdue_invoices', '=', True)
        ])

        for contract in contracts_to_reactivate:
            _logger.info(f"Reactivando servicio para contrato {contract.name}...")
            # GEMINI: Llamar a la función de reactivación de servicio en silver_provisioning
            # contract.action_reactivate_service() # Esta función debe ser implementada
            contract.write({'state_service': 'active'}) # Placeholder

        _logger.info("Cron Job: Corte y Reconexión Automática de Contratos finalizado.")


    def write(self, vals):
        # GEMINI: Lógica para liberar la ONU descubierta cuando el servicio se desactiva.
        if 'state_service' in vals:
            deactivating_states = ['suspended', 'removal_list', 'removed']
            if vals['state_service'] in deactivating_states:
                for contract in self:
                    # Buscamos si este contrato tiene una ONU descubierta asignada.
                    # Es importante buscar en el modelo correcto.
                    discovered_onu = self.env['silver.olt.discovered.onu'].search([
                        ('contract_id', '=', contract.id)
                    ], limit=1)
                    
                    if discovered_onu:
                        # Si la encontramos, la "liberamos" para que pueda ser
                        # seleccionada por otro contrato o eliminada en el próximo descubrimiento.
                        # En este caso, la eliminamos directamente como se solicitó.
                        discovered_onu.write({'contract_id': None})

        print(("write0", vals))
        return super(SilverContract, self).write(vals)
