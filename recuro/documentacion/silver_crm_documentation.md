# Documentación del Módulo: silver_crm

## 1. Visión General y Estratégica

**silver_crm** adapta el potente CRM de Odoo a las necesidades específicas de un Proveedor de Servicios de Internet (ISP). Transforma el flujo de ventas tradicional en un flujo de **factibilidad técnica**, donde la venta depende de la cobertura de red.

El módulo permite a los equipos de ventas validar la disponibilidad de servicio antes de cerrar una oportunidad, seleccionando el nodo y la caja NAP más cercanos geográficamente al cliente potencial.

### 1.1. Objetivos de Negocio

*   **Validación de Factibilidad en Tiempo Real:** Permitir a los vendedores saber si un cliente es conectable sin esperar a una visita técnica fallida.
*   **Geomarketing:** Ubicar leads en el mapa para identificar zonas de alta demanda ("zonas calientes").
*   **Automatización del Cierre:** Convertir automáticamente una oportunidad ganada en un contrato borrador, traspasando toda la información técnica y comercial.

## 2. Alcance Funcional

### 2.1. Extensiones a `crm.lead` (Iniciativa/Oportunidad)

El modelo `crm.lead` se enriquece con campos técnicos críticos:

*   **Ubicación del Servicio:**
    *   `silver_address_id`: Dirección normalizada del cliente (del módulo `silver_base`).
    *   `node_id`: Nodo de red seleccionado.
    *   `box_id`: Caja NAP seleccionada para la conexión.
    *   `zone_id`: Zona geográfica (heredada del nodo o dirección).

*   **Definición del Producto:**
    *   `type_service_id`: Tipo de servicio (Internet, TV).
    *   `plan_type_id`: Tipo de plan (Residencial, Corporativo).
    *   `product_id`: El plan de velocidad específico a contratar.

*   **Vínculo Contractual:**
    *   `contract_id`: Enlace al contrato generado tras ganar la oportunidad.

## 3. Herramientas y Flujos de Trabajo

### 3.1. Wizard "Encontrar Nodos Cercanos" (`action_open_find_node_wizard`)
Esta herramienta calcula la distancia geodésica (fórmula Haversine) entre la dirección del cliente y todos los nodos de la red activos.
*   **Input:** Coordenadas del Lead.
*   **Proceso:** Itera sobre `silver.node` calculando distancias.
*   **Output:** Lista de los 10 nodos más cercanos ordenados por distancia, permitiendo al vendedor elegir el óptimo.

### 3.2. Selector de Caja NAP (`action_open_nap_map`)
Abre una vista de mapa especializada que muestra:
*   La ubicación del cliente.
*   Las cajas NAP del nodo seleccionado.
*   Permite seleccionar visualmente la caja con puertos libres más cercana.

### 3.3. Conversión a Contrato (`action_create_contract`)
Al marcar una oportunidad como "Ganada" (o mediante botón manual), el sistema:
1.  Valida que todos los datos técnicos (Dirección, Plan, Caja NAP) estén completos.
2.  Crea un nuevo `silver.contract` en estado Borrador.
3.  Crea la línea de servicio (`silver.contract.line`) con el precio del producto seleccionado.
4.  Vincula el contrato al Lead para trazabilidad.

## 4. Instalación y Dependencias

*   **Dependencias:**
    *   `crm` (Odoo estándar)
    *   `silver_base` (Para direcciones)
    *   `silver_product` (Para planes)
    *   `silver_network` (Para nodos y cajas)
    *   `silver_contract` (Para la creación del contrato)
