# Documentación del Módulo: silver_l10n_ve (Suite)

## 1. Visión General y Estratégica

La suite **`silver_l10n_ve`** adapta Odoo a las regulaciones fiscales, contables y territoriales de Venezuela. Dado que Odoo estándar carece de una localización venezolana profunda para la versión Enterprise más reciente, estos módulos llenan el vacío crítico para la operación legal de un ISP en el país.

El enfoque es **modular**, separando la base territorial de la lógica de facturación electrónica y los reportes contables.

### 1.1. Objetivos de Negocio

*   **Cumplimiento Legal (SENIAT):** Asegurar que las facturas, retenciones y libros de compra/venta cumplan con la normativa vigente.
*   **Precisión Territorial:** Permitir la segmentación de clientes por Estado, Municipio y Parroquia (esencial para impuestos municipales y logística).
*   **Facturación Electrónica:** Integración agnóstica con proveedores de facturación electrónica.

## 2. Arquitectura de Módulos

La solución se divide en capas:

1.  **`silver_l10n_ve_base` (Núcleo Territorial):**
    *   Define la división política de Venezuela: Estados, Municipios, Parroquias y Ciudades.
    *   Extiende `res.partner` y `silver.address` para incluir estos campos.
    *   Valida el formato del RIF (Registro de Información Fiscal).

2.  **`silver_l10n_ve_accounting` (Contabilidad):**
    *   Configura el Plan de Cuentas (Chart of Accounts) venezolano.
    *   Gestiona los impuestos (IVA, IGTF, Retenciones ISLR/IVA).

3.  **`silver_l10n_ve_electronic_invoice` (Facturación):**
    *   Gestiona la emisión de documentos fiscales electrónicos.
    *   Es "agnóstico" al proveedor: define una interfaz común para que módulos conectores (ej. `TheFactory`, `Sistematics`) se enchufen sin cambiar la lógica del ERP.

4.  **`silver_l10n_ve_sale_purchase` (Libros):**
    *   Genera los Libros de Compra y Venta requeridos por el SENIAT.

## 3. Alcance Funcional Detallado

### 3.1. Gestión de Direcciones (`silver_l10n_ve_base`)

Este módulo modifica el comportamiento estándar de las direcciones en Odoo. En lugar de campos de texto libre para ciudad o estado, fuerza la selección de:

*   **Estado** (`res.country.state`): Ej. Zulia, Miranda.
*   **Municipio** (`res.country.municipality`): Ej. Maracaibo, Chacao.
*   **Parroquia** (`res.country.parish`): Ej. Olegario Villalobos.

Esta estructura se inyecta en el modelo `silver.address`, asegurando que cada instalación de fibra óptica tenga una ubicación fiscalmente válida.

### 3.2. Validación de RIF

El sistema incluye validaciones para asegurar que el RIF (V, J, G, E, P) tenga el formato correcto y el dígito verificador válido, evitando errores en la facturación que podrían acarrear multas.

### 3.3. Facturación Electrónica

El módulo `silver_l10n_ve_electronic_invoice` actúa como un *middleware*.
*   No se conecta directamente a un servicio.
*   Provee los campos necesarios en la factura (`nro_control`, `fecha_comprobante`).
*   Define el flujo de aprobación: Borrador -> Publicado -> **Enviado a Proveedor** -> Aprobado/Rechazado.

## 4. Dependencias

*   **Base:** `silver_base` (Para la integración con direcciones Silver).
*   **Contabilidad:** `account` (Odoo Enterprise/Community).
*   **Externa:** `l10n_ve_location` (Módulo comunitario OCA o similar que provee la data inicial de estados/municipios, si aplica).
