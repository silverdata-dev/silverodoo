# Documentación del Módulo: silver_product

## 1. Visión General y Estratégica

**silver_product** adapta el catálogo de productos estándar de Odoo para soportar la complejidad de los servicios de telecomunicaciones. Un "producto" en Odoo ya no es solo un ítem vendible, sino una definición técnica de un servicio (Perfil de Velocidad, Recurrencia, Tecnología).

Este módulo es el puente entre lo que se vende (Facturación/Ventas) y lo que se entrega técnicamente (Ancho de banda, QoS).

### 1.1. Objetivos de Negocio

*   **Definición de Planes:** Configurar velocidades de subida/bajada y precios.
*   **Control de Hardware:** Gestionar modelos de equipos (ONUs, Routers) como productos almacenables.
*   **Integración Técnica:** Almacenar parámetros de configuración (VLANs, Burst Limit, Prioridad) directamente en la ficha del producto.

## 2. Alcance Funcional

### 2.1. Extensiones a `product.template`

El módulo añade pestañas y campos específicos para ISP al formulario de producto:

*   **Datos ISP (Técnicos):**
    *   `is_internet`: Flag para identificar planes de datos.
    *   **Ancho de Banda:** `upload_bandwidth`, `download_bandwidth` (en Mbps).
    *   **Bursting (Ráfaga):** Configuración avanzada de `burst_limit`, `burst_threshold` y `burst_time` para MikroTik/OLT queues.
    *   **QoS:** `queue_priority`.
    *   **Perfiles OLT:** `traffic_profile_index`, `profile_radius`.

*   **Configuración de Servicio:**
    *   `service_type_id`: Clasificación del servicio (Internet, VoIP, IPTV).
    *   `recurring_invoices_ok`: Indica si este producto genera facturas recurrentes (suscripción).

*   **Gestión de Hardware:**
    *   `hardware_model_id`: Vincula el producto comercial con una especificación de hardware (ej. "Huawei HG8546M").
    *   `brand_id`: Marca del fabricante.

### 2.2. Modelos Auxiliares

*   **`product.brand`:** Gestión de fabricantes (Huawei, ZTE, TP-Link).
*   **`silver.hardware.model`:** Especificaciones técnicas de modelos de equipos.
*   **`silver.service.type`:** Categorización de servicios (Internet, Instalación, TV).

## 3. Relación con Otros Módulos

*   **`silver_contract`:** Los contratos instancian estos productos. Al crear una línea de contrato, se copian o referencian los parámetros de velocidad definidos aquí.
*   **`silver_provisioning`:** Al aprovisionar una ONU, el sistema lee el `upload_bandwidth` y `download_bandwidth` del producto para configurar los Traffic Profiles o Service Profiles en la OLT.
*   **`stock`:** Los productos de tipo hardware (`is_storable`) se gestionan en el inventario estándar de Odoo (números de serie, lotes).

## 4. Instalación y Dependencias

*   **Dependencias:**
    *   `product` (Odoo estándar)
    *   `stock` (Para gestión de hardware)
    *   `silver_base`