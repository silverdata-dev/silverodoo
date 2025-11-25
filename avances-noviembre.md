# Informe de Avances del Proyecto SilverData Odoo (ISP) - Noviembre 2025

**Fecha:** 24 de Noviembre de 2025
**Versión:** Odoo 17.0
**Estado:** En desarrollo activo / Fase de Integración Técnica

## 1. Resumen Ejecutivo
El proyecto ha establecido una arquitectura modular sólida para la gestión de un ISP (Proveedor de Servicios de Internet), separando claramente la lógica comercial (`silver_contract`) de la técnica (`silver_provisioning`, `silver_network`) y la localización venezolana (`silver_l10n_ve_*`). 

El núcleo comercial (contratos, facturación recurrente) muestra un nivel de madurez alto. El núcleo técnico (provisionamiento, conexión con OLTs) está funcional pero requiere refinamiento y limpieza de código para pasar a producción.

## 2. Análisis de lo Realizado (Lo Hecho)

### A. Arquitectura y Módulos
Se ha implementado una estructura de módulos personalizada que evita el "código espagueti", facilitando el mantenimiento futuro:
- **`silver_base`**: Cimientos comunes.
- **`silver_contract`**: El corazón administrativo. Maneja el ciclo de vida del cliente.
- **`silver_isp_management`**: Extensión de lógica ISP.
- **`silver_provisioning`**: Puente entre Venta y Técnica. Incluye lógica de conexión a hardware.
- **`silver_network`**: Modelado de la red física (Nodos, OLTs, Cajas NAP).
- **Localización**: Integración desacoplada con `odoo-venezuela` a través de módulos puente (`silver_l10n_ve_*`).

### B. Funcionalidades Clave Implementadas
1.  **Gestión de Contratos (`silver_contract`)**:
    - Máquina de estados completa: Borrador -> Abierto -> Activo -> Cerrado.
    - Estados del servicio independientes: Activo/Suspendido/Terminado.
    - Lógica de facturación recurrente (Prepago/Postpago) con soporte para ciclos de corte.
    - Motor de promociones, descuentos y pagos anticipados.
    - Promesas de pago y manejo de referidos.

2.  **Infraestructura Técnica (`silver_network` / `silver_provisioning`)**:
    - Inventario de red: OLTs, Tarjetas, Puertos, ONUs, Cajas de dispersión (Splitters).
    - Lógica de descubrimiento de ONUs: Comandos para interactuar con OLTs (aparentemente Huawei/ZTE) mediante CLI (`show onu auto-find`).
    - Asignación de recursos: VLANs, IPs, Puertos.

3.  **Localización**:
    - Integración preparada para Facturación, IGTF y Retenciones de Venezuela.

## 3. Hoja de Ruta: Siguientes Pasos

### A. Inmediato (Esta semana / Próximo Sprint)
El foco debe ser la **estabilidad técnica y limpieza de código**.

1.  **Refactorización de `silver_provisioning`**:
    - **Limpieza**: Eliminar `print()` de depuración en `silver_provisioning/models/silver_olt.py`.
    - **Robustez**: Mejorar el manejo de errores en la conexión SSH/Telnet (`silver_network`). Actualmente, el parseo de salida de la OLT es manual y puede ser frágil ante cambios de firmware.
    - **Estandarización**: Asegurar que todas las excepciones de usuario usen `odoo.exceptions.UserError`.

2.  **Revisión de Migración Odoo 17**:
    - Verificar que no queden remanentes de atributos obsoletos como `attrs` en las vistas XML. Odoo 17 usa `invisible="condition"`, `readonly="condition"`, etc. Una mezcla de ambos puede causar errores de interfaz silenciosos.

3.  **Prueba de Flujo Completo (End-to-End)**:
    - Realizar una prueba "Lead a Factura": Crear Prospecto -> Validar Factibilidad -> Firmar Contrato -> Provisionar ONU (Simulado) -> Generar primera Factura.

### B. Mediano Plazo (Diciembre - Enero)
Consolidación operativa y reportes.

1.  **Automatización de Cortes y Reconexiones**:
    - Implementar los Cron Jobs (acciones planificadas) que lean el estado de los pagos y ejecuten comandos de suspensión/activación en las OLTs automáticamente.
2.  **Portal de Cliente**:
    - Habilitar vistas en el portal web para que el cliente vea su consumo, facturas y reporte pagos.
3.  **Integración Contable Fina**:
    - Verificar que los asientos contables de la facturación recurrente (especialmente los diferidos o anticipados) se generen correctamente según la normativa venezolana.

### C. Largo Plazo (Q1 2026)
Escalabilidad y Valor Agregado.

1.  **Monitoreo (Zabbix/Grafana)**:
    - Integrar alertas de caída de servicio directamente en la ficha del cliente en Odoo.
2.  **App Móvil de Técnicos**:
    - Una interfaz simplificada para que los instaladores cierren órdenes de trabajo y escaneen seriales de ONUs desde el celular.
3.  **CRM Avanzado**:
    - Automatización de marketing basada en el comportamiento de pago o consumo del cliente.

## 4. Notas Técnicas para el Desarrollador
- **Atención**: Revisar `silver_provisioning/models/silver_olt.py`. La lógica de parseo de `show onu auto-find` depende de posiciones fijas de caracteres. Considerar usar expresiones regulares (Regex) para mayor seguridad.
- **TODO**: Hay un pendiente en `silver_geo/controllers/nodes.py` sobre el filtrado de assets por nodo que debe resolverse antes de desplegar mapas masivos.

---
*Generado por Asistente Gemini CLI*
