# Documentación del Módulo: silver_network

## 1. Visión General y Estratégica

**silver_network** (a veces referido como ISP Management) es el módulo encargado de modelar la infraestructura física y lógica de la red de telecomunicaciones. Actúa como el inventario técnico de la empresa, registrando desde los equipos centrales (Core, OLT) hasta la última milla (Cajas NAP, Splitters).

Este módulo es la base sobre la cual `silver_provisioning` ejecuta comandos. Sin `silver_network`, el sistema no "conoce" la red.

### 1.1. Objetivos de Negocio

*   **Inventario de Red Preciso:** Saber exactamente qué equipos se tienen, dónde están instalados y cuál es su capacidad (puertos libres vs ocupados).
*   **Gestión de Capacidad:** Prevenir la sobreventa de puertos en OLTs o Cajas NAP.
*   **Modelado de Topología:** Representar la jerarquía de la red: Nodo -> OLT -> Tarjeta -> Puerto PON -> Splitter -> Caja NAP.

## 2. Modelos de Datos Principales

El módulo utiliza herencia de `silver.asset` y `silver.netdev` para compartir características comunes (números de serie, IPs de gestión).

### 2.1. Estructura Jerárquica

1.  **`silver.node` (Nodo):**
    *   Punto de presencia físico (Data Center, Torre, Caseta).
    *   Agrupa equipos (Cores, OLTs).
    *   Contiene estadísticas de capacidad (`olt_count`, `core_count`).

2.  **`silver.core` (Equipo Core):**
    *   Router de borde o concentrador (ej. Mikrotik, Huawei NE).
    *   Gestiona la autenticación (RADIUS) y el enrutamiento.

3.  **`silver.olt` (Optical Line Terminal):**
    *   Equipo de cabecera GPON/EPON.
    *   Hereda de `silver.netdev` para gestión de conexión (IP, usuario, password, driver).
    *   Contiene `silver.olt.card` (Tarjetas) y `silver.olt.card.port` (Puertos PON).
    *   **Funcionalidad Clave:** Generación automática de estructura de tarjetas/puertos basada en configuración de slots (`action_generar`).

4.  **`silver.box` (Caja NAP):**
    *   Punto de acceso final para la acometida del cliente.
    *   Ubicada geográficamente (`latitude`, `longitude`) para validación de cobertura en CRM.

5.  **`silver.splitter`:**
    *   Elemento pasivo de división óptica.

## 3. Funcionalidad Técnica

### 3.1. Gestión de OLTs
El modelo `silver.olt` es rico en lógica:
*   **Conexión de Prueba (`action_connect_olt`):** Verifica credenciales Telnet/SSH y recupera el Hostname.
*   **Generación de Estructura:** Crea automáticamente los registros de tarjetas y puertos en Odoo según la configuración física definida (número de slots y puertos por tarjeta).

### 3.2. Gestión de Nodos
*   Centraliza la vista de todos los activos en una ubicación geográfica.
*   Punto de entrada para crear infraestructura asociada (Botones "Crear OLT", "Crear Core").

## 4. Instalación y Dependencias

*   **Dependencias:**
    *   `mail` (Odoo estándar)
    *   `silver_base` (Para zonas y direcciones)
    *   `silver_product` (Algunos equipos pueden estar vinculados a modelos de hardware)
