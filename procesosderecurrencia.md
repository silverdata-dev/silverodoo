# Documentación Maestra de Procesos de Recurrencia y Ciclo de Vida de Contratos (ISP)

**Versión:** 1.0
**Fecha:** 2023-10-27

## Parte 1: Visión Estratégica y de Negocio (Para Gerencia y Líderes de Equipo)

### 1.1. Propósito y Objetivos de Negocio

Este sistema está diseñado para ser el motor central que gestiona los ingresos recurrentes de la compañía. Su propósito es automatizar de extremo a extremo el ciclo de vida financiero y de servicio del cliente, desde su alta hasta su baja.

Los **objetivos estratégicos** que cumple son:
1.  **Maximizar la Eficiencia Operativa:** Eliminar el 95% de la intervención manual en los procesos de facturación, cobro y gestión de servicios.
2.  **Asegurar la Previsibilidad del Flujo de Caja:** Garantizar que la facturación se ejecute de manera puntual y sistemática, y que la gestión de la morosidad sea proactiva y automática.
3.  **Mejorar la Experiencia del Cliente (CX):** Ofrecer un servicio transparente, con facturación clara (incluso con prorrateos) y reactivación inmediata del servicio tras el pago, eliminando fricciones.
4.  **Fomentar la Escalabilidad:** Permitir que la empresa crezca en número de clientes sin necesidad de un crecimiento lineal en el personal administrativo y de soporte.
5.  **Flexibilidad Comercial:** Soportar diferentes planes, ciclos de facturación, promociones y cambios de plan sin requerir desarrollos adicionales.

### 1.2. Indicadores Clave de Rendimiento (KPIs) Impactados
Este sistema permite medir y mejorar directamente los siguientes KPIs:
*   **Ingreso Mensual Recurrente (MRR):** El sistema es la fuente de verdad para el cálculo del MRR.
*   **Tasa de Abandono (Churn Rate):** La automatización y la buena experiencia reducen el churn involuntario (por problemas de pago).
*   **Días de Venta Pendientes de Cobro (DSO):** La gestión automática de la morosidad acelera los cobros.
*   **Coste de Adquisición de Cliente (CAC):** La eficiencia operativa reduce los costes, impactando indirectamente el CAC a largo plazo.
*   **Lifetime Value (LTV):** Un ciclo de vida de cliente más largo y eficiente aumenta el LTV.

---

## Parte 2: Arquitectura Funcional y Flujos de Proceso

### 2.1. Diagrama de Estados del Contrato

Este diagrama ilustra los posibles estados de un contrato y las transiciones entre ellos.

```mermaid
stateDiagram-v2
    [*] --> Borrador: Creación Manual

    Borrador --> Activo: Activación Inicial
    note right on Borrador
        Aquí se calcula el
        primer prorrateo si
        la activación no coincide
        con el inicio del ciclo.
    end note

    Activo --> Suspendido: Cron de Suspensión
    note left on Activo
        Ciclo normal de facturación.
        El contrato permanece aquí
        mientras el cliente pague
        a tiempo.
    end note

    Suspendido --> Activo: Evento de Pago
    note right on Suspendido
        El servicio está interrumpido.
        El sistema espera el pago
        de TODAS las deudas vencidas.
    end note

    Activo --> Cancelado: Solicitud de Baja
    Suspendido --> Cancelado: Baja por Deuda Crónica
    Borrador --> Cancelado: Anulación

    Cancelado --> [*]
```

### 2.2. Flujo Detallado del Ciclo de Vida

#### A. Creación y Activación de un Contrato (con Prorrateo)
1.  **Creación:** Un operador crea un nuevo contrato en estado "Borrador". Se asigna un plan (`silver.plan`) y una política de corte (`silver.cutoff.date`), que define el día del mes para la facturación (ej. día 1, 15 o 25).
2.  **Activación:** Al activar el contrato:
    *   El sistema verifica si la fecha de activación coincide con el día de corte.
    *   **Si no coincide**, se calcula un **prorrateo**.
        *   **Fórmula:** `(Precio Mensual del Plan / Días del Mes) * Días Restantes hasta el Próximo Corte`.
        *   Este monto se almacena como un "cargo pendiente" que se añadirá a la **primera factura recurrente**.
    *   Se establece la `fecha del próximo corte` (`next_invoice_date`) según la política.

#### B. Ciclo de Facturación Recurrente
*   **Disparador:** Cron diario (`_cron_generate_invoices`).
*   **Lógica:**
    1.  El cron busca contratos `Activos` con `next_invoice_date <= hoy`.
    2.  Para cada contrato, crea una factura (`account.move`).
    3.  **Puebla la factura con:**
        *   La línea de cargo correspondiente al plan del mes/periodo actual.
        *   **Cualquier cargo pendiente por prorrateos** (de activación o cambios de plan).
        *   **Cualquier cargo único** (ej. una visita técnica) registrado en el contrato.
    4.  Valida la factura (`action_post`).
    5.  **Gestión de Pagos Adelantados:** Si el cliente tiene crédito a favor (saldo positivo en su cuenta de partner), el sistema intenta conciliar la nueva factura contra ese crédito automáticamente.
    6.  Actualiza la `next_invoice_date` para el siguiente ciclo.

#### C. Gestión de Morosidad y Suspensión
*   **Disparador:** Cron diario (`_cron_check_suspensions`).
*   **Lógica:**
    1.  Busca contratos `Activos` que tengan al menos una factura con `invoice_date_due < hoy` y `payment_state != 'paid'`.
    2.  Para cada contrato encontrado, invoca el método `action_suspend()`.
    3.  El método cambia el estado a `Suspendido` y dispara una llamada a la **API del sistema de provisión** para efectuar el corte técnico del servicio.

#### D. Gestión de Pagos y Reactivación
*   **Disparador:** Evento de escritura en `account.move` cuando `payment_state` cambia a `'paid'`.
*   **Lógica:**
    1.  El sistema identifica el contrato (`contract_id`) asociado a la factura pagada.
    2.  Si el contrato está `Suspendido`:
    3.  **Verificación exhaustiva:** El sistema comprueba si existen **OTRAS** facturas para ese mismo contrato que sigan vencidas y no pagadas.
    4.  **Solo si TODAS las deudas vencidas están saldadas**, invoca el método `action_reactivate()`.
    5.  El método cambia el estado a `Activo` y dispara una llamada a la **API del sistema de provisión** para la reconexión.

#### E. Cambio de Plan (Upgrade/Downgrade)
1.  **Disparador:** Acción manual de un operador en el contrato.
2.  **Lógica:**
    *   Se invoca un asistente (`wizard`) para el cambio de plan.
    *   **Cálculo de Ajustes (Prorrateo dual):**
        1.  **Crédito:** Se calcula un crédito por la porción no utilizada del plan antiguo. `(Precio Plan Antiguo / Días del Periodo) * Días Restantes`.
        2.  **Débito:** Se calcula un cargo por la porción a utilizar del nuevo plan. `(Precio Plan Nuevo / Días del Periodo) * Días Restantes`.
    *   El **neto** de estos dos montos se guarda como un "cargo pendiente" que se incluirá en la **próxima factura recurrente**.
    *   El contrato se actualiza con la referencia al nuevo plan para futuros ciclos de facturación.

---

## Parte 3: Guía Técnica Detallada (Para Equipo de Desarrollo)

### 3.1. Modelos de Datos Principales

*   **`contract.contract`**
    *   `plan_id`: `Many2one('silver.plan')` - El plan de servicio actual.
    *   `cutoff_policy_id`: `Many2one('silver.cutoff.date')` - Define el día de facturación.
    *   `state`: `Selection` (`draft`, `active`, `suspended`, `cancelled`).
    *   `next_invoice_date`: `Date` - Campo clave para el cron de facturación.
    *   `one_time_charge_ids`: `One2many('contract.charge')` - Para cargos únicos.
    *   `proration_charge_ids`: `One2many('contract.charge')` - Para cargos de prorrateo.

*   **`silver.plan`**
    *   `name`: `Char`.
    *   `price`: `Float`.
    *   `billing_cycle`: `Selection` (`monthly`, `quarterly`, `yearly`).

*   **`account.move`**
    *   `contract_id`: `Many2one('contract.contract')` - **Campo crítico para la trazabilidad**. Debe ser indexado.

### 3.2. Lógica de Métodos Clave (Pseudo-código)

```python
# En models/contract_contract.py

def _cron_generate_invoices(self):
    # Busca contratos listos para facturar
    contracts_to_invoice = self.env['contract.contract'].search([
        ('state', '=', 'active'),
        ('next_invoice_date', '<=', fields.Date.today())
    ])

    for contract in contracts_to_invoice:
        invoice_lines = []

        # 1. Añadir línea del plan recurrente
        plan = contract.plan_id
        invoice_lines.append((0, 0, {
            'name': f"Servicio {plan.name} - Periodo {fields.Date.today()}",
            'price_unit': plan.price,
        }))

        # 2. Añadir cargos pendientes (prorrateos, etc.)
        pending_charges = contract.proration_charge_ids.filtered(lambda c: not c.invoiced)
        for charge in pending_charges:
            invoice_lines.append((0, 0, {
                'name': charge.description,
                'price_unit': charge.amount,
            }))
            charge.invoiced = True # Marcar como facturado

        # 3. Crear y validar la factura
        invoice = self.env['account.move'].create({
            'partner_id': contract.partner_id.id,
            'move_type': 'out_invoice',
            'contract_id': contract.id, # Trazabilidad
            'invoice_line_ids': invoice_lines,
        })
        invoice.action_post()

        # 4. (Opcional) Aplicar crédito existente
        # Odoo puede hacer esto automáticamente si la configuración es correcta

        # 5. Actualizar fecha del próximo corte
        contract.next_invoice_date = contract._calculate_next_invoice_date()

def action_change_plan(self, new_plan_id):
    # Lógica del prorrateo dual
    credit_amount = self._calculate_proration(self.plan_id, 'credit')
    debit_amount = self._calculate_proration(new_plan_id, 'debit')
    net_amount = debit_amount - credit_amount

    # Crear un cargo pendiente
    self.env['contract.charge'].create({
        'contract_id': self.id,
        'amount': net_amount,
        'description': f"Ajuste por cambio de plan a {new_plan_id.name}",
    })

    # Actualizar el plan en el contrato
    self.plan_id = new_plan_id

# En models/account_move.py (heredado)

def write(self, vals):
    res = super(AccountMove, self).write(vals)
    if 'payment_state' in vals and vals['payment_state'] == 'paid':
        for invoice in self:
            if invoice.contract_id and invoice.contract_id.state == 'suspended':
                # Verificar si hay OTRAS deudas
                other_due_invoices = self.search([
                    ('contract_id', '=', invoice.contract_id.id),
                    ('id', '!=', invoice.id),
                    ('payment_state', '!=', 'paid'),
                    ('invoice_date_due', '<', fields.Date.today())
                ])
                if not other_due_invoices:
                    invoice.contract_id.action_reactivate()
    return res
```

---

## Parte 4: Guía de Operaciones (Para Equipo de Soporte y Seguimiento)

### Escenario 1: Cliente llama, servicio suspendido.
1.  **Diagnóstico:** Busca el contrato del cliente. El estado será **"Suspendido"**.
2.  **Acción:** Ve a la pestaña "Facturas" del contrato. Informa al cliente el **monto total adeudado** (suma de todas las facturas "No Pagadas").
3.  **Explicación Clave:** "El sistema reactivará su servicio de forma automática tan pronto como nuestro departamento de contabilidad registre el pago de **toda** la deuda pendiente. No es necesario que nos vuelva a llamar después de pagar."

### Escenario 2: Cliente quiere cambiar de plan.
1.  **Acción:** En el contrato del cliente, utiliza el botón/asistente "Cambiar Plan". Selecciona el nuevo plan deseado.
2.  **Explicación Clave:** "Perfecto, su plan ha sido cambiado. En su **próxima factura**, verá un pequeño ajuste. Le acreditaremos los días que no usó de su plan anterior y le cobraremos los días que usará del nuevo plan en este ciclo. A partir del siguiente mes, ya verá el precio normal del nuevo plan."

### Escenario 3: Cliente pagó pero sigue suspendido.
1.  **Diagnóstico:**
    *   **Causa A (Más común):** El pago aún no ha sido procesado por Contabilidad. En la factura, el estado sigue siendo "No Pagado". Pide al cliente el comprobante y pásalo a Contabilidad.
    *   **Causa B (Menos común):** El cliente solo pagó una de varias facturas vencidas. Explícale que la reactivación solo ocurre al saldar **toda** la deuda.
    *   **Causa C (Rara/Excepción):** Todas las facturas están "Pagadas" pero el contrato sigue "Suspendido". **Esto es una anomalía.** Escala el caso inmediatamente al equipo de desarrollo con el ID del contrato.

---

## Parte 5: Guía de Procesos (Para Equipo de Contabilidad)

### 5.1. Impacto en el Flujo de Trabajo
Vuestro proceso central no cambia, pero su impacto se magnifica.

*   **Facturas Generadas Automáticamente:** Ya no necesitáis crear las facturas recurrentes. El sistema las generará y las dejará en estado "Publicada", listas para ser enviadas y gestionadas.
*   **Conciliación es la Clave:** Vuestra acción de conciliar un pago y marcar una factura como "Pagado" es el **disparador directo** de la reactivación de servicios. La puntualidad en la conciliación es crítica para la experiencia del cliente.

### 5.2. Gestión de Pagos Adelantados y Créditos
*   **Escenario:** Un cliente paga de más o paga antes de que se emita la factura.
*   **Proceso Odoo Estándar:** Al registrar el pago, si no hay una factura con la cual conciliarlo, Odoo lo registrará como un **crédito a favor** del cliente (un "pago por adelantado").
*   **Acción del Sistema:** Cuando el cron genere la siguiente factura para ese cliente, el sistema (o el contable, según configuración) podrá usar ese crédito para pagar total o parcialmente la nueva factura. **No se requiere ninguna acción especial** más allá del proceso contable estándar.

### 5.3. Facturas con Prorrateos
*   Veréis facturas que contienen, además de la línea del plan mensual, una o más líneas adicionales con descripciones como "Ajuste por activación" o "Ajuste por cambio de plan". Estos montos son calculados automáticamente. No requieren verificación manual, pero es bueno que entendáis su origen para responder a posibles consultas de clientes.
