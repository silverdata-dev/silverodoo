# Documentación del Módulo: silver_base

## 1. Visión General y Estratégica

**silver_base** es el módulo fundacional de la vertical ISP de SilverData. Su propósito no es ofrecer funcionalidad final al usuario, sino establecer los cimientos de datos geográficos y estructurales sobre los que se construyen los módulos de negocio (`contract`, `network`, `crm`).

Su principal aportación es un modelo de direccionamiento granular y jerárquico (`silver.address`) que sustituye o extiende la gestión de direcciones plana de Odoo estándar, permitiendo la precisión GPS necesaria para el despliegue de redes de fibra óptica.

### 1.1. Objetivos Técnicos

*   **Normalización Geográfica:** Evitar la duplicidad y ambigüedad en las direcciones de instalación.
*   **Geolocalización Nativa:** Incorporar latitud y longitud como ciudadanos de primera clase en la ficha del cliente y en la infraestructura.
*   **Centralización de Configuración:** Almacenar configuraciones transversales para la suite ISP.

## 2. Modelos de Datos Principales

### 2.1. `silver.address` (Dirección Silver)
Es la entidad central del módulo. A diferencia de un campo de texto simple, una dirección Silver es un objeto con entidad propia.

*   **Jerarquía:** Soporta relaciones padre-hijo (ej. Edificio -> Piso -> Apartamento).
*   **Campos Clave:**
    *   `name`: Nombre completo generado automáticamente.
    *   `street`, `building`, `house_number`: Componentes de la dirección.
    *   `zone_id`: Vínculo con la zona geográfica.
    *   `latitude`, `longitude`: Coordenadas GPS con alta precisión (7 decimales).
    *   `parent_id`: Dirección contenedora.

### 2.2. `silver.zone` (Zona)
Representa un área geográfica o administrativa (Sector, Urbanización, Barrio). Permite agrupar direcciones y nodos para análisis de cobertura.

### 2.3. Extensiones a `res.partner`
El módulo extiende el modelo de contactos estándar para vincularlo con `silver.address`. Esto asegura que cada cliente tenga una ubicación normalizada compatible con los mapas de cobertura.

## 3. Dependencias

Este módulo no tiene dependencias funcionales externas, pero es **dependencia obligatoria** para:
*   `silver_crm`
*   `silver_contract`
*   `silver_network`
