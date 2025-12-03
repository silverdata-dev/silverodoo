# Documentación del Módulo: silver_contract

## 1. Visión General y Estratégica

**silver_contract** es el corazón administrativo de la suite ISP. Gestiona el acuerdo legal y comercial entre la empresa y el suscriptor. Orquesta el ciclo de vida del servicio, controlando cuándo se factura, cuándo se corta el servicio y qué equipos tiene el cliente en custodia.

A diferencia de las suscripciones estándar de Odoo, este módulo está diseñado para manejar la lógica de "Corte por Falta de Pago" y "Reconexión", así como la prorrata en la primera factura.

### 1.1. Objetivos de Negocio

*   **Ciclo de Vida Completo:** Alta -> Suspensión -> Reconexión -> Baja -> Retiro de Equipos.
*   **Facturación Recurrente Flexible:** Soporte para pospago, prepago, ciclos de facturación personalizados y prorrateo automático.
*   **Trazabilidad:** Historial unificado de facturas, tickets, movimientos de stock y cambios técnicos asociados al contrato.

## 2. Modelos de Datos Principales

### 2.1. `silver.contract` (Contrato)
Es el maestro de suscripción.

*   **Estados del Contrato (`state`):**
    *   `Draft` (Borrador): Preparación.
    *   `Open` (En Proceso): Aprobado administrativamente, pendiente de instalación.
    *   `Active` (Activo): Servicio funcionando y facturando.
    *   `Closed` (Cerrado): Contrato finalizado.

*   **Estados del Servicio (`state_service`):**
    *   `Active`: Navegando.
    *   `Suspended`: Corte por falta de pago (Soft cut).
    *   `Disabled`: Corte administrativo/técnico (Hard cut).
    *   `Removal List`: Pendiente de retiro de equipos.

*   **Campos Clave:**
    *   `partner_id`: Cliente.
    *   `silver_address_id`: Dirección de instalación (crítico para soporte técnico).
    *   `plan_type_id`, `service_type_id`: Segmentación comercial.
    *   `recurring_next_date`: Fecha de la próxima factura automática.
    *   `cutoff_date_id`: Política de corte (día de pago, días de gracia).

### 2.2. `silver.contract.line` (Líneas de Servicio)
Detalla qué se está cobrando.
*   Vincula con `product.product`.
*   Define el precio unitario y cantidad.
*   Distingue entre líneas recurrentes (Plan de Internet) y de cargo único (Instalación, Router vendido).

## 3. Flujos de Trabajo Críticos

### 3.1. Activación del Contrato (`start_contract`)
1.  El contrato pasa a estado `Active`.
2.  **Cálculo de Prorrata:** Si el servicio inicia a mitad de mes y la política lo dicta, genera una línea de cargo único por los días restantes.
3.  **Programación de Facturación:** Establece la `recurring_next_date` basándose en el día de corte configurado.

### 3.2. Facturación Recurrente (`_cron_generate_invoices`)
Un proceso programado (Cron Job) corre diariamente:
1.  Busca contratos activos cuya `recurring_next_date` sea hoy.
2.  Genera una Factura (`account.move`) en estado Borrador o Publicado.
3.  Avanza la fecha de próxima facturación (ej. +1 mes).

### 3.3. Suspensión Automática (`_cron_auto_suspend...`)
1.  Detecta facturas vencidas según los días de gracia del contrato.
2.  Cambia `state_service` a `Suspended`.
3.  Dispara trigger hacia `silver_provisioning` para cortar el servicio en la OLT/Mikrotik.

## 4. Integración con Módulos Satélites

*   **`silver_helpdesk_contract`:** Permite ver el estado del servicio y tickets desde el contrato.
*   **`silver_network` / `silver_provisioning`:** El contrato almacena los IDs técnicos (`onu_id`, `ip_address`) asignados durante el aprovisionamiento.
*   **`silver_l10n_ve`:** Integra campos de localización venezolana si está instalado.

## 5. Instalación y Dependencias

*   **Dependencias:**
    *   `silver_base`
    *   `silver_product`
    *   `account` (Facturación Odoo)
    *   `silver_network` (Opcional, pero recomendado para ISP)