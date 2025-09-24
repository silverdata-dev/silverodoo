
# Documentación del Módulo: silver_product

## 1. Visión General y Estratégica

El módulo **silver_product** es un componente central del ecosistema SilverData Odoo. Su propósito principal es definir y gestionar el catálogo de servicios y planes que la empresa ofrece a sus clientes. Este módulo no gestiona productos físicos en inventario, sino los servicios de conectividad que se comercializan.

### 1.1. Objetivos de Negocio

*   **Centralizar el Catálogo de Servicios:** Proporcionar una única fuente de verdad para todos los planes y servicios ofrecidos, con sus respectivas velocidades, precios y condiciones.
*   **Facilitar la Venta y Contratación:** Permitir que los módulos de Ventas (`silver_sales`) y Contratos (`silver_contract`) consuman una lista estandarizada de productos para agilizar el proceso de alta de clientes.
*   **Flexibilizar la Oferta Comercial:** Permitir la rápida creación y modificación de planes para adaptarse a las necesidades del mercado y a las estrategias de la empresa.

## 2. Alcance Funcional

El alcance de `silver_product` se centra en el modelado de los servicios de ISP.

### 2.1. Modelos de Datos Principales

*   **`product.template` (Plantilla de Producto):**
    *   **Propósito:** Define las características generales de un tipo de servicio.
    *   **Campos Clave:**
        *   `name`: Nombre del plan (e.g., "Plan Fibra Hogar 100 Mbps").
        *   `list_price`: Precio base del servicio.
        *   `type`: Definido como "Servicio".
        *   Atributos específicos del ISP (e.g., velocidad de subida, velocidad de bajada, tipo de tecnología).

*   **`product.product` (Producto Variante):**
    *   **Propósito:** Representa una versión específica de un plan que un cliente puede contratar. En el contexto de SilverData, este es el modelo que se vincula directamente a un contrato.
    *   **Relación:** Hereda de `product.template` y se utiliza en el modelo `isp.contract`.

## 3. Relaciones con Otros Módulos

`silver_product` es un módulo fundamental que se integra con varios otros componentes del sistema:

*   **`silver_contract` (Contratos):**
    *   El modelo `isp.contract` tiene una relación directa con `product.product`. Cada contrato está asociado a un plan específico, que define las condiciones del servicio, incluyendo el precio que se usará para la facturación.

*   **`silver_sales` (Ventas):**
    *   El equipo de ventas utiliza el catálogo de productos para crear cotizaciones (`sale.order`) y oportunidades (`crm.lead`). La disponibilidad técnica de un servicio en una zona específica se valida contra la infraestructura (`silver_isp`) antes de que la venta se cierre.

*   **`silver_billing` (Facturación):**
    *   La facturación recurrente se genera a partir de la información del plan (`product.product`) asociado al contrato del cliente. El precio, los impuestos y los ciclos de facturación dependen de la configuración del producto.

*   **`silver_provisioning` (Aprovisionamiento):**
    *   Aunque la relación no es directa, los atributos del producto (como la velocidad) son utilizados por el módulo de aprovisionamiento para configurar los equipos de red (OLTs, RADIUS) cuando se activa un contrato.

## 4. Flujos de Trabajo

1.  **Creación de un Plan:**
    *   Un administrador o gerente de producto crea una nueva `product.template` para definir un nuevo servicio (e.g., "Plan Gamer Pro").
    *   Se especifican los atributos clave: nombre, precio, velocidades, etc.
    *   Odoo crea automáticamente una `product.product` asociada.

2.  **Venta y Contratación:**
    *   Un vendedor selecciona una `product.product` del catálogo al crear una cotización para un cliente.
    *   Una vez aprobada, se genera un `isp.contract` vinculado a ese producto.

3.  **Activación y Facturación:**
    *   El contrato utiliza la información del producto para disparar el aprovisionamiento y para generar la primera factura.

## 5. Indicadores Clave de Rendimiento (KPIs)

*   **Número de planes activos:** Cantidad de productos de tipo servicio que están disponibles para la venta.
*   **Margen por plan:** Rentabilidad de cada producto, calculada a partir de su precio de venta y los costos asociados.
*   **% de productos sin precio:** Un indicador de calidad de datos para asegurar que todos los servicios en el catálogo tengan un precio definido.
