# Documentación del Módulo: silver_helpdesk y Satélites

## 1. Visión General y Estratégica

La suite de módulos **Silver Helpdesk** representa una arquitectura modular diseñada para gestionar las solicitudes de soporte técnico, incidentes, cambios comerciales y mantenimientos dentro de SilverData Odoo. 

A diferencia de un sistema de tickets monolítico, esta solución desacopla la lógica en un módulo base (`silver_helpdesk`) y múltiples módulos de integración satelitales. Esto permite una escalabilidad sostenible, donde cada área operativa (Contratos, Red, Inventario, IPTV, Localización) se integra de manera limpia sin sobrecargar el núcleo del sistema.

### 1.1. Objetivos de Negocio

*   **Modularidad y Mantenibilidad:** Evitar dependencias cíclicas y permitir la actualización independiente de funcionalidades (ej. actualizar la lógica de inventario sin afectar la lógica de facturación).
*   **Gestión Unificada de Procesos:** Unificar flujos técnicos (averías, lentitud) y comerciales (cambio de plan, cambio de titular) bajo un mismo modelo de datos (`helpdesk.ticket`), pero con comportamientos especializados.
*   **Automatización de Flujos:** Integrar acciones automáticas (cambio de velocidad en la OLT, generación de facturas, movimiento de stock) directamente desde las etapas del ticket.
*   **Trazabilidad Total:** Mantener un registro histórico de cambios de dirección, equipos y planes asociados a cada ticket.

## 2. Arquitectura del Sistema

La solución se compone de un núcleo y cinco módulos de integración:

1.  **`silver_helpdesk` (Base):** 
    *   Define el motor de **Workflows** (Flujos de trabajo).
    *   Gestiona los **Tipos de Ticket** (`silver.ticket.type`) y la configuración de etapas (`silver.ticket.stage.config`).
    *   No tiene dependencias de contratos o red, sirviendo como cimiento puro.

2.  **`silver_helpdesk_contract` (Integración Comercial):**
    *   Vincula el ticket con el contrato (`silver.contract`).
    *   Maneja procesos comerciales: Cambio de Plan, Suspensión, Cambio de Titular, Facturación de servicios desde el ticket.
    *   Gestiona los estados del servicio (`state_service`) visualizados en el ticket.

3.  **`silver_helpdesk_isp` (Integración Técnica/Red):**
    *   Conecta el ticket con la infraestructura física (`silver_network`).
    *   Permite la gestión de cambios de equipos (ONUs, Routers), cambios de domicilio (puertos NAP, OLTs) y asignación de IPs.
    *   Mantiene los datos técnicos "Actuales" vs "Nuevos" para facilitar migraciones.

4.  **`silver_helpdesk_stock` (Integración Logística):**
    *   Gestiona el consumo de materiales y equipos (`stock.lot`) directamente en el ticket.
    *   Permite la asignación de equipos "Extra" (Mesh, Repetidores) y su control de inventario.

5.  **`silver_helpdesk_iptv` (Integración Multimedia):**
    *   Maneja la activación, desactivación y promoción de servicios de TV/OTT.

6.  **`silver_helpdesk_l10n_ve` (Localización Venezuela):**
    *   Añade campos específicos para la dirección en Venezuela (Estado, Municipio, Parroquia, Referencias detalladas) adaptando el ticket a la realidad local.

## 3. Alcance Funcional por Módulo

### 3.1. Silver Helpdesk (Base)

*   **Modelo Principal:** `helpdesk.ticket` (heredado).
*   **Motor de Workflow:**
    *   **`silver.ticket.type`:** Define la categoría macro del proceso (ej. "Cambio de Plan", "Soporte Técnico").
    *   **`silver.ticket.stage.config`:** Permite definir qué sucede cuando un ticket entra en una etapa específica (ej. Ejecutar un Server Action, restringir a un Grupo de Usuarios).
*   **Funcionalidad Clave:** Permite que un mismo sistema de estados (Borrador -> En Proceso -> Resuelto) se comporte diferente según el tipo de ticket.

### 3.2. Silver Helpdesk Contract (Comercial)

*   **Vínculo con Contrato:** El campo `contract_id` es central. Toda la información del cliente se hereda de allí.
*   **Procesos Comerciales Soportados:**
    *   **Cambio de Plan:** Permite seleccionar un `new_plan_id`.
    *   **Cambio de Suspensión:** Planificación de suspensiones temporales.
    *   **Cambio de Titular:** Transferencia de responsabilidad del contrato.
    *   **Facturación:** Flags como `is_invoice_service` permiten generar facturas (Invoice) desde el ticket por servicios prestados (visitas técnicas, reparaciones).
*   **Estados del Servicio:** Visualización mediante *Ribbons* (Cintas de colores) del estado actual del servicio (Activo, Cortado, Suspendido) directamente en la cabecera del ticket.

### 3.3. Silver Helpdesk ISP (Técnico)

*   **Gestión de Infraestructura:**
    *   Campos para `node_id`, `box_id`, `olt_id`, `olt_port_id`, etc.
*   **Lógica de "Old" vs "New":**
    *   Para procesos de mudanza (`is_change_address`), el sistema almacena la ubicación técnica anterior (ej. `node_id_old`) y la nueva propuesta (`node_id`), permitiendo realizar el cambio lógico y físico sin perder el historial.
*   **Gestión de Equipos (CPEs):**
    *   Soporta el cambio de ONUs y Routers.
    *   Campos para seriales que entran (`serial_onu_new`) y salen (`serial_onu_back`).
    *   Integración con Pools de IP dinámicas y estáticas.

### 3.4. Silver Helpdesk Stock (Inventario)

*   **Modelo:** `helpdesk.stock.line`.
*   **Funcionalidad:**
    *   Lista de materiales consumidos en la resolución del ticket (cables, conectores).
    *   Gestión de equipos recuperados (retirada de servicio).
    *   Trazabilidad de números de serie (`stock.lot`) para equipos instalados.

## 4. Flujos de Trabajo Críticos (Ejemplos)

### 4.1. Flujo de Cambio de Domicilio (Mudanza)

1.  **Creación:** Se crea un ticket con Tipo de Proceso "Cambio de Domicilio".
2.  **Datos Actuales:** El sistema carga automáticamente la dirección y datos técnicos (Nodo A, Caja A) actuales en los campos `_old`.
3.  **Nueva Factibilidad:** El técnico selecciona la nueva dirección y los nuevos datos técnicos (Nodo B, Caja B) en la pestaña "Cambio Domicilio".
4.  **Ejecución:** Al avanzar el ticket a la etapa "Realizado", el sistema (mediante Server Actions configurados en el Workflow base) actualiza el `silver.contract` con la nueva dirección y libera los recursos del Nodo A.

### 4.2. Flujo de Cambio de Plan

1.  **Solicitud:** El cliente solicita aumento de velocidad. Se crea ticket "Cambio de Plan".
2.  **Selección:** Se selecciona el `new_plan_id` (Producto Odoo).
3.  **Aprovisionamiento:** El sistema valida la factibilidad técnica del nuevo plan.
4.  **Cierre:** Al cerrar el ticket, se actualiza la línea del contrato y se reconfigura la velocidad en la OLT (vía integración con `silver_provisioning`, si está instalado).

## 5. Instalación y Dependencias

Para desplegar esta funcionalidad correctamente, se debe respetar el siguiente orden de instalación debido a la herencia de modelos:

1.  **`helpdesk_mgmt`** (Módulo base de la OCA).
2.  **`silver_helpdesk`** (Núcleo del Workflow).
3.  **`silver_helpdesk_contract`** (Depende de 1 y 2).
4.  **`silver_helpdesk_isp`** (Depende de `silver_network` y 3).
5.  **`silver_helpdesk_stock`** (Depende de `stock` y 3).
6.  **`silver_helpdesk_iptv`** (Depende de 3).
7.  **`silver_helpdesk_l10n_ve`** (Depende de 4 y `silver_l10n_ve_base`).

---
**Nota Técnica:** Esta refactorización elimina la necesidad del módulo monolítico `silver_ticket` antiguo. Asegúrese de desinstalarlo antes de desplegar esta suite para evitar conflictos de nombres en las vistas XML.
