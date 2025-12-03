# Documentación del Módulo: silver_unms (Gestión de Agenda)

## 1. Visión General y Estratégica

**`silver_unms`** (a veces llamado "Calendario de Instalaciones") es un módulo de productividad diseñado para coordinar a las cuadrillas técnicas en terreno.

A pesar de su nombre (que hace referencia al sistema de gestión de Ubiquiti), en este contexto de Odoo funciona como un **despachador de órdenes de trabajo** visual. Utiliza una vista de línea de tiempo (*Timeline*) para mostrar la disponibilidad de los técnicos y asignar oportunidades de instalación o reparaciones de manera eficiente.

### 1.1. Objetivos de Negocio

*   **Optimización de Rutas:** Agrupar instalaciones por **Zona** y **Nodo** para minimizar el desplazamiento de los técnicos.
*   **Visibilidad de Capacidad:** Ver claramente qué técnicos ("Instaladores") están libres en una franja horaria específica.
*   **Drag & Drop:** Reagendar citas simplemente arrastrando la barra de tiempo en la pantalla.

## 2. Modelos de Datos Principales

### 2.1. `silver.assignment` (Asignación / Instalador)
Representa a un recurso técnico (una persona o una cuadrilla) disponible para realizar trabajos.
*   **Vínculo con Usuario:** `user_id` conecta con el usuario de sistema Odoo.
*   **Restricciones Geográficas:**
    *   `zone_ids`: Zonas donde este técnico puede trabajar.
    *   `node_ids`: Nodos específicos que atiende.
*   **Visualización:** Campo `color` para diferenciar técnicos en el calendario.

### 2.2. Integración con `crm.lead`
El módulo extiende la Oportunidad/Iniciativa para añadir:
*   `assignment_id`: El técnico asignado.
*   `schedule_start` / `schedule_stop`: Fecha y hora agendada.

## 3. Funcionalidad Clave: La Vista Timeline

El módulo implementa una vista personalizada basada en `web_timeline`.

### 3.1. Agrupación Inteligente
La vista no muestra una lista plana. Agrupa las tareas primero por **Zona** y luego por **Asignación (Técnico)**.
*   Esto permite al coordinador ver: *"¿Quién está disponible hoy en la Zona Norte?"*.

### 3.2. Modo Fantasma ("Ghost Mode")
Una limitación técnica de las vistas timeline es que ocultan las filas vacías. Si un técnico no tiene trabajo hoy, desaparece de la vista, impidiendo asignarle tareas nuevas.
*   **Solución:** Al crear un `silver.assignment`, el sistema genera automáticamente un registro "Placeholder" (Fantasma) en el año 1980.
*   **Efecto:** Esto fuerza a Odoo a renderizar la línea del técnico siempre, permitiendo arrastrar nuevas tareas hacia él.

## 4. Flujos de Trabajo

1.  **Venta:** Un vendedor gana una oportunidad en `silver_crm`.
2.  **Agendamiento:** El coordinador de operaciones abre la vista Timeline de `silver_unms`.
3.  **Asignación:** Busca la oportunidad (que aparece en una lista de "No asignados" o en una fecha tentativa) y la arrastra a la fila del técnico correspondiente a la zona del cliente.
4.  **Ejecución:** El técnico ve la cita en su calendario y procede a la instalación.

## 5. Instalación y Dependencias

*   **Dependencias:**
    *   `crm` (Gestión de oportunidades).
    *   `web_timeline` (Librería de visualización OCA).
    *   `silver_base` (Zonas).
    *   `silver_crm` (Integración con el flujo de venta).
