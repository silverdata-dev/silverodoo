# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SilverCutoffDate(models.Model):
    _name = 'silver.cutoff.date'
    _description = 'Periodo de Consumo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # --- Campos Principales ---
    name = fields.Char(string='Descripción', required=True)
    active = fields.Boolean(string='Activo', default=True)
    plan_type_id = fields.Many2one('silver.plan.type', string='Tipo de plan', required=True)
    recurring_invoicing_type = fields.Selection([('prepaid', 'Prepago'), ('postpaid', 'Postpago')], string='Tipo de facturación', required=True, default='postpaid')

    # --- Campos del Formulario (extraídos de periodoconsumo.txt) ---
    
    # Cabecera y Botones
    contract_actives = fields.Integer(string="Contratos Activos", compute="_compute_contract_actives") # Campo calculado
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True) # Campo calculado
    
    # Grupo Principal
    type_cut = fields.Selection([('days', 'Por Día de corte'), ('date', 'Por Fecha de inicio del contrato')], string='Forma de Corte', default='date', required=True)
    day_cut = fields.Integer(string='Día de Corte')
    month_grace = fields.Selection([('1', 'Días de gracia'), ('2', 'Mes de gracia')], string='Día/Mes de Gracia')
    days_grace = fields.Integer(string='Días de Gracia')
    publish_invoices = fields.Boolean(string='¿Publicar Facturas?')
    is_invoice_debts = fields.Boolean(string='Deudas en Factura')
    is_draft_invoices = fields.Boolean(string='Facturas en Borrador')
    is_active_umbral = fields.Boolean(string='Activar Umbral')
    amount_exempt_cut = fields.Float(string='Monto Exento de Corte')
    is_cutoff_service = fields.Boolean(string='Realizar cortes')
    is_skip_cutoff = fields.Boolean(string='Omitir cortes')
    date_cut = fields.Date(string='Fecha de Corte', readonly=True)
    last_month = fields.Integer(string='Mes Actual de Corte', readonly=True)

    # Pestaña: Configuraciones Generales
    day_consumption = fields.Integer(string='Día de Consumo')
    days_grace_comsumption = fields.Integer(string='Días para Mes Anticipado')
    date_from = fields.Date(string='Fecha desde', readonly=True)
    date_to = fields.Date(string='Hasta', readonly=True)
    month_comsumption = fields.Integer(string='Mes de Consumo', readonly=True)
    type_period = fields.Selection([('monthly', 'Mensual'), ('yearly', 'Anual')], string='Período')
    is_apportion = fields.Boolean(string='¿Prorratear?')
    apportion_next_date = fields.Boolean(string='Prorrateo siguiente fecha')
    is_round_up = fields.Boolean(string='Prorrateo con Redondeo Superior')
    invoice_advance_month = fields.Boolean(string='No facturar prorrateo mes anticipado')
    day_from_prorate = fields.Integer(string='Proratear desde')
    day_to_prorate = fields.Integer(string='Proratear hasta')
    has_iptv_discount = fields.Boolean(string='Aplicar prorrateo en IPTV')
    is_day_start = fields.Boolean(string='Por dia de inicio')
    day_invoice = fields.Integer(string='Día de Facturación')
    type_date_invoice = fields.Selection([('due_date', 'Fecha de Vencimiento'), ('invoice_date', 'Fecha de Factura')], string='Tipo')
    is_fac_extra_value = fields.Boolean(string='¿Facturar solo valores extra?')
    is_fac_material_extra = fields.Boolean(string='¿Facturar Materiales extras?')
    is_select_journal_invoice = fields.Boolean(string='¿Escoger diario de Factura?')
    make_invoice_bolivares = fields.Boolean(string='¿Facturar valores en Bolivares?')
    advance_invoice = fields.Boolean(string='Facturación Anticipada')
    date_invoice = fields.Date(string='Fecha de Facturación', readonly=True)
    is_preinvoice = fields.Boolean(string='Generar Avisos de Cobro')
    is_invoice_posted = fields.Boolean(string='Facturas Publicadas')
    journal_preinvoice_id = fields.Many2one('account.journal', string='Diario')
    is_preinvoice_active = fields.Boolean(string='Aviso de Cobro Contratos Activos')
    is_preinvoice_removal_list = fields.Boolean(string='Aviso de Cobro Contratos Lista Retiro')
    payment_promise_day_cut = fields.Integer(string='Días Plazo para Promesas de Pago')
    is_apply_active_ct = fields.Boolean(string='Aplicar CT Activos')
    pay_promise_day_cut = fields.Integer(string='Días Plazo para Promesas de Pago Abonos')

    # Pestaña: Reconexiones
    is_aditional_preinvoice = fields.Boolean(string='Prefactura Adicional')
    reconnection_policy = fields.Selection([('full_payment', 'Pago Completo'), ('partial_payment', 'Pago Parcial')], string='Politica de Reconexión')
    apply_reconnection = fields.Boolean(string='Activar Reconexion')
    is_reconnection_required = fields.Boolean(string='Reconexión obligatoria')
    is_not_apply_cutoff = fields.Boolean(string='No aplica cortados')
    is_proration_cutoff = fields.Boolean(string='Prorrateo cortados')
    charge_proration = fields.Boolean(string='Cobrar Prorrateo')
    charge_reconection_portal = fields.Boolean(string='Aplicar Reconexion Portal')
    is_status_removal_list = fields.Boolean(string='Lista de Retiro')
    is_status_disabled = fields.Boolean(string='Cortados')
    days_without_proration = fields.Boolean(string='Dias sin prorrateo')
    number_days_without_proration = fields.Integer(string='Rango reconexión prorrateo')
    reconnection_type = fields.Selection([('manual', 'Manual'), ('auto', 'Automática'), ('static', 'Estática')], string='Tipo de reconexión')
    day_reconnection_from = fields.Integer(string='Rango reconexión desde')
    day_reconnection_to = fields.Integer(string='Rango reconexión hasta')
    day_reconnection_rl_from = fields.Integer(string='Rango reconexión desde')
    day_reconnection_rl_to = fields.Integer(string='Rango reconexión hasta')

    # Pestaña: Omitir Cortes
    is_cutoff_friday = fields.Boolean(string='Viernes')
    is_cutoff_saturday = fields.Boolean(string='Sábado')
    is_cutoff_sunday = fields.Boolean(string='Domingo')
    is_cutoff_monday = fields.Boolean(string='Lunes')
    contract_days_cutoff_line_ids = fields.One2many('contract.days.cutoff.line', 'cutoff_date_id', string='Líneas de Días de Corte')

    # Pestaña: Notificaciones
    is_active_contract_mail = fields.Boolean(string='Not.Bienvenida Mail')
    is_preinvoice_mail = fields.Boolean(string='Not.Avisos de Cobro Mail')
    is_cutoff_mail = fields.Boolean(string='Not.Cortes Mail')
    is_send_preinvoice_mail = fields.Boolean(string='Not.Link Aviso de Cobro Mail')
    is_payment_mail = fields.Boolean(string='Not.Pagos Mail')
    is_removal_list_mail = fields.Boolean(string='Not.Lista Retiro Mail')
    color = fields.Integer(string='Índice de color')
    is_amount_due_cutoff_mail = fields.Boolean(string='Not.Cortes Mail')
    day_cutoff_recursive_mail = fields.Integer(string='Nro.Dias Despues')
    is_amount_due_mail = fields.Boolean(string='Not.Deudas Mail')
    day_recursive_mail = fields.Integer(string='Nro.Dias Antes')
    quantity_recursive_mail = fields.Integer(string='Cantidad Dias')
    is_outstanding_debts = fields.Boolean(string='Deudas sin vencer')
    is_active_contract_wp = fields.Boolean(string='Not.Bienvenida WP')
    is_preinvoice_wp = fields.Boolean(string='Not.Prefactura WP')
    is_payment_wp = fields.Boolean(string='Not.Pagos WP')
    is_amount_due_wp = fields.Boolean(string='Not.Deudas WP')
    is_cutoff_wp = fields.Boolean(string='Not.Cortes WP')
    is_removal_list_wp = fields.Boolean(string='Not.Lista Retiro WP')
    is_send_preinvoice_wp = fields.Boolean(string='Not.Link Prefactura WP')
    is_end_date_shipping = fields.Boolean(string='Dia maximo de pago fija')
    end_date_shipping = fields.Integer(string='Dia máximo de pago')
    template_active_contract_wp = fields.Many2one('contract.template.wp', string='Tmp.Bienvenida WP')
    template_preinvoice_wp = fields.Many2one('contract.template.wp', string='Tmp.Prefactura WP')
    template_payment_wp = fields.Many2one('contract.template.wp', string='Tmp.Pagos WP')
    template_amount_due_wp = fields.Many2one('contract.template.wp', string='Tmp.Deudas WP')
    template_cutoff_wp = fields.Many2one('contract.template.wp', string='Tmp.Cortes WP')
    template_removal_list_wp = fields.Many2one('contract.template.wp', string='Tmp.Lista Retiro WP')
    template_send_preinvoice_wp = fields.Many2one('contract.template.wp', string='Tmp.Link Prefactura WP')
    is_amount_due_cutoff_wp = fields.Boolean(string='Not.Cortes WP')
    day_cutoff_recursive_wp = fields.Integer(string='Nro.Dias Despues')
    is_amount_due_recursive_wp = fields.Boolean(string='Not.Deudas WP')
    day_recursive_wp = fields.Integer(string='Nro.Dias Antes')
    quantity_recursive_wp = fields.Integer(string='Cantidad Dias')
    
    # Pestaña: Otros
    is_payment_selected_journal = fields.Boolean(string='Pagos con diarios seleccionados')
    days_cut_benefit = fields.Selection([('1', '1 día'), ('2', '2 días')], string='Dias adicionales')
    additional_users = fields.Boolean(string='Usuarios Adicionales')
    is_accumulate_discounts = fields.Boolean(string='Acumular descuentos')
    journal_benefits_ids = fields.Many2many('account.journal', string='Diarios beneficiarios')
    date_cut_with_benefit = fields.Date(string='Fecha de Corte con Beneficios', readonly=True)


    @api.onchange('plan_type_id')
    def _onchange_plan_type_id(self):
        if self.plan_type_id:
            # Acceder al valor original antes del cambio
            #original_plan_name = self._origin.plan_type_id.name
            # Si el nombre está vacío o es igual al nombre del tipo de plan anterior
            #if not self.name or self.name == original_plan_name:
            self.name = self.plan_type_id.name

    # --- Métodos Calculados ---
    def _compute_contract_actives(self):
        # Esta es una implementación de ejemplo. Debería ser ajustada a la lógica de negocio real.
        for record in self:
            record.contract_actives = self.env['silver.contract'].search_count([('cutoff_date_id', '=', record.id), ('state', '=', 'open')])

    @api.depends('day_cut', 'day_consumption', 'name', 'day_invoice', 'recurring_invoicing_type')
    def _compute_display_name(self):
        for record in self:
            r = []
            if record.recurring_invoicing_type:
                r.append(
                {'prepaid':'Prepago', 'postpaid':'Postpago'}[record.recurring_invoicing_type]
                )
            if record.name: r.append(record.name)
            if record.type_cut == 'days': r.append('Consumo Fecha Inicio')
            if record.type_cut == 'date':
                r.append('Consumo '+str(record.day_consumption))
                r.append('Corte ' + str(record.day_cut))
            #if record.day_invoice:
            r.append('Facturación ' + str(record.day_invoice))
            record.display_name = "/".join(r)

    def is_cutoff_date(self, contract_start_date, check_date):
        """
        Verifica si una fecha dada es una fecha de corte según la configuración.
        :param contract_start_date: Fecha de inicio del contrato (objeto date).
        :param check_date: Fecha a verificar (objeto date).
        :return: True si es una fecha de corte, False en caso contrario.
        """
        self.ensure_one()

        # 1. Si se omiten todos los cortes, no es fecha de corte.
        if self.is_skip_cutoff:
            return False

        # 2. Determinar el día de corte del mes.
        cutoff_day = 0
        if self.type_cut == 'days':
            cutoff_day = self.day_cut
        elif self.type_cut == 'date':
            cutoff_day = contract_start_date.day
        
        # Si no hay un día de corte válido, no se puede procesar.
        if not (1 <= cutoff_day <= 31):
            return False

        # 3. Comprobar si el día de la fecha a verificar coincide con el día de corte.
        if check_date.day != cutoff_day:
            return False

        # 4. Comprobar si el día de la semana está marcado para ser omitido.
        # weekday(): Lunes=0, Martes=1, ..., Domingo=6
        weekday = check_date.weekday()
        if self.is_cutoff_monday and weekday == 0:
            return False
        if self.is_cutoff_friday and weekday == 4:
            return False
        if self.is_cutoff_saturday and weekday == 5:
            return False
        if self.is_cutoff_sunday and weekday == 6:
            return False
            
        # 5. Si pasó todas las verificaciones, es una fecha de corte.
        return True

    def action_update_contract_date_cut(self):
        # Lógica para el botón
        pass

    def action_update_date_invoice(self):
        # Lógica para el botón
        pass

    def action_open_contract(self):
        # Lógica para el botón
        pass
