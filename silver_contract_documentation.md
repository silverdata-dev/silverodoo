
# Documentación del Módulo: silver_contract

## 1. Visión General y Estratégica

El módulo **silver_contract** es el núcleo de la gestión del ciclo de vida del cliente en SilverData Odoo. Su función principal es administrar los acuerdos de servicio con los clientes, desde el alta inicial hasta la baja, pasando por suspensiones, cambios de plan y reconexiones.

Este módulo vincula la información comercial (cliente y plan) con la infraestructura técnica (puertos de red), convirtiéndose en el eje central que orquesta las operaciones.

### 1.1. Objetivos de Negocio

*   **Gestionar el Ciclo de Vida del Cliente:** Centralizar y automatizar todas las etapas de la relación con el cliente (alta, baja, suspensión, cambio de plan).
*   **Asegurar la Integridad de los Datos:** Garantizar que cada servicio activo esté correctamente asociado a un cliente, un plan y un recurso de red físico.
*   **Automatizar el Aprovisionamiento:** Servir como disparador (`trigger`) para los flujos de aprovisionamiento técnico en la red.
*   **Facilitar la Facturación Precisa:** Proporcionar al módulo de facturación (`silver_billing`) la información necesaria para generar facturas recurrentes correctas.

## 2. Alcance Funcional

El módulo se centra en el modelo `isp.contract` y sus interacciones con el resto del sistema.

### 2.1. Modelos de Datos Principales

*   **`isp.contract` (Contrato):**
    *   **Propósito:** Representa el acuerdo de servicio activo de un cliente. Es el registro principal que une al cliente, el servicio contratado y los recursos de red asignados.
    *   **Campos Clave:**
        *   `name`: Identificador único del contrato.
        *   `partner_id`: Relación con el cliente (`res.partner`).
        *   `product_id`: Relación con el plan o servicio contratado (`product.product`).
        *   `state`: Estado del contrato (e.g., "Borrador", "Activo", "Suspendido", "Cancelado").
        *   `olt_port_id`: Puerto de la OLT asignado (si aplica).
        *   `splitter_id`: Puerto del splitter asignado.
        *   `onu_id`: Relación con el equipo CPE/ONU asignado al cliente (`isp.onu`).
        *   `radius_user_id`: Vínculo al usuario RADIUS generado para la autenticación.

## 3. Relaciones con Otros Módulos

`silver_contract` es un módulo de alta interconectividad:

*   **`silver_product` (Productos):**
    *   Cada contrato debe estar asociado a un `product.product` que define el plan, la velocidad y el precio del servicio.

*   **`silver_isp` (Infraestructura):**
    *   El contrato se enlaza directamente con los recursos de la red física, como `isp.olt.card.port` y `isp.splitter`. Esta relación es crucial para la validación de factibilidad y la reserva de puertos.

*   **`silver_provisioning` (Aprovisionamiento):**
    *   El cambio de estado de un contrato (e.g., de "Borrador" a "Activo") dispara los flujos de trabajo en `silver_provisioning` para crear el usuario RADIUS, configurar la OLT y activar el servicio.

*   **`silver_billing` (Facturación):**
    *   El módulo de facturación lee los contratos activos para generar las facturas periódicas. Las suspensiones por morosidad actualizan el estado del contrato.

*   **`silver_inventory` (Inventario):**
    *   El contrato está vinculado al equipo (`isp.onu` o `isp.cpe`) que se instala en la ubicación del cliente.

## 4. Flujos de Trabajo Críticos

1.  **Alta de Cliente:**
    *   Se crea un nuevo registro en `isp.contract`.
    *   Se asocia un cliente (`res.partner`) y un plan (`product.product`).
    *   Se realiza una **validación de factibilidad** consultando la disponibilidad de puertos en `silver_isp`.
    *   Si hay factibilidad, se reservan los puertos y se pasa el contrato a estado "Activo".
    *   Este cambio de estado notifica a `silver_provisioning` para que configure la red.

2.  **Suspensión por Morosidad:**
    *   El módulo `silver_billing` detecta una factura vencida.
    *   Se invoca un proceso que cambia el estado del `isp.contract` a "Suspendido".
    *   Este cambio de estado dispara un flujo en `silver_provisioning` para enviar un comando de desconexión (CoA) a través de RADIUS o para desactivar el puerto en la OLT.

3.  **Baja del Servicio:**
    *   Un operador cambia el estado del contrato a "Cancelado".
    *   Se liberan los recursos de red (`isp.olt.card.port`, `isp.splitter`) que estaban asignados.
    *   Se dispara un flujo para eliminar al usuario de RADIUS y desconfigurar el puerto de la OLT.

## 5. Indicadores Clave de Rendimiento (KPIs)

*   **Churn (Tasa de Abandono):** Porcentaje de contratos que pasan a estado "Cancelado" en un período determinado.
*   **Tiempo Medio de Provisión (MTTP):** Tiempo transcurrido desde que se crea el contrato hasta que el servicio está efectivamente activo para el cliente.
*   **Número de Reconexiones:** Cantidad de contratos que pasan de "Suspendido" a "Activo", indicando la efectividad de los procesos de cobranza.
