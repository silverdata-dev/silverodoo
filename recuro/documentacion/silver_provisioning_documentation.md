# Documentación del Módulo: silver_provisioning

## 1. Visión General y Estratégica

**silver_provisioning** es el "cerebro ejecutor" de la suite ISP. Mientras que `silver_network` define *qué* equipos existen, `silver_provisioning` define *cómo* hablar con ellos y *qué* hacer.

Este módulo implementa la lógica de conexión (Telnet, SSH, API), los drivers por marca (Huawei, ZTE, V-SOL, Mikrotik) y las automatizaciones que configuran los equipos remotamente cuando ocurren eventos comerciales (ej. activar un contrato).

### 1.1. Objetivos Técnicos

*   **Abstracción de Hardware:** Permitir que los operadores activen servicios sin conocer los comandos CLI específicos de cada marca.
*   **Automatización Zero-Touch:** Aprovisionar ONUs y configurar Routers automáticamente.
*   **Sincronización Bidireccional:** Leer el estado real de la red (Discovery) y escribir la configuración deseada (Provisioning).

## 2. Alcance Funcional

### 2.1. Extensiones a `silver.olt`
El módulo inyecta la lógica de control en el modelo de OLT definido en `silver_network`:

*   **Descubrimiento de ONUs (`action_discover_onus`):**
    *   Se conecta a la OLT.
    *   Ejecuta comandos de "auto-find" (ej. `show onu auto-find`).
    *   Parsea la salida de texto crudo.
    *   Crea o actualiza registros en `silver.olt.discovered.onu`.
    *   Filtra ONUs ya aprovisionadas para mostrar solo las nuevas.

*   **Sincronización Manual (`action_sync_olt_manual`):**
    *   Aplica cambios masivos de configuración (ej. cambiar DNS, perfiles de velocidad) a todas las ONUs activas de una OLT.

*   **Métodos de Aprovisionamiento (`_provision_onu_*`):**
    *   `_provision_onu_base`: Asocia la ONU al puerto PON, asigna TCONT, Gemport y VLANs.
    *   `_provision_onu_wan`: Configura la WAN IP (PPPoE/DHCP/Static) dentro de la ONU (Tr-069/OMCI).
    *   `_provision_onu_wifi`: Configura SSID y Password remotamente.

### 2.2. Gestión de Comandos y Logs
El método `_execute_with_logging` es el núcleo transaccional:
1.  Abre conexión con el driver adecuado.
2.  Envía la secuencia de comandos.
3.  Captura la respuesta.
4.  **Logging:** Escribe un registro detallado (comando enviado + respuesta recibida) en el Chatter (muro de mensajes) del contrato asociado. Esto es vital para auditoría y debugging.
5.  Manejo de Errores: Si un comando falla, intenta un rollback o lanza una excepción clara al usuario.

### 2.3. Modelos de Soporte
*   **`silver.olt.discovered.onu`:** Tabla temporal para ONUs conectadas físicamente pero no dadas de alta en el sistema.
*   **Wizards:** Asistentes para seleccionar una ONU descubierta y asignarla a un contrato.

## 3. Flujos de Trabajo Críticos

### 3.1. Alta de Servicio (Provisioning)
1.  Desde el contrato (`silver.contract`), se selecciona "Activar".
2.  El sistema busca una ONU descubierta (o permite ingresar serial manual).
3.  `silver_provisioning` se conecta a la OLT.
4.  Ejecuta la secuencia de alta (Profile -> Tcont -> Gemport -> Service Port).
5.  Si es exitoso, cambia el estado del contrato a "Activo" y guarda el log.

### 3.2. Corte y Reconexión
1.  Al suspender un contrato, se invoca `disable_onu`.
2.  El módulo envía el comando de desactivación administrativa al puerto de la ONU.
3.  Al reactivar, se envía el comando inverso.

## 4. Instalación y Dependencias

*   **Dependencias:**
    *   `silver_network` (Hereda sus modelos).
    *   `silver_contract` (Interactúa con el estado del contrato).
    *   **Librerías Python:** Requiere `paramiko` o librerías similares para conexiones SSH/Telnet (generalmente manejadas en `silver_netdev`).