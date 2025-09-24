
# Documentación del Módulo: silver_provisioning

## 1. Visión General y Estratégica

El módulo **silver_provisioning** (también referido como `silver_netops` en la documentación) no es un módulo de Odoo con modelos propios, sino un **conjunto de flujos de trabajo, lógica de negocio y conectores** responsables de la automatización y gestión remota de la infraestructura de red. Su propósito es traducir las acciones de negocio (como activar un contrato) en comandos técnicos ejecutados en los equipos de red.

Actúa como la capa de orquestación entre la gestión de Odoo y la red física y lógica.

### 1.1. Objetivos de Negocio

*   **Automatizar el Aprovisionamiento:** Eliminar la intervención manual en la activación, suspensión y modificación de servicios, reduciendo el tiempo de provisión y los errores humanos.
*   **Garantizar la Consistencia:** Asegurar que la configuración en los equipos de red (RADIUS, OLTs, Routers) refleje fielmente el estado de los contratos en Odoo.
*   **Centralizar la Gestión de Red:** Proporcionar un punto único desde el cual se disparan las operaciones de red, facilitando la auditoría y la trazabilidad.
*   **Mejorar la Fiabilidad:** Implementar mecanismos robustos como reintentos y colas para manejar fallos en la comunicación con los equipos de red.

## 2. Alcance Funcional y Componentes

`silver_provisioning` se compone principalmente de lógica de automatización, wizards y conectores.

### 2.1. Lógica de Automatización (Workers/Colas)

*   **Propósito:** Ejecutar tareas de red de forma asíncrona para no bloquear la interfaz de Odoo. Estas tareas son gestionadas por un sistema de colas (como Odoo Jobs o un sistema externo como Celery).
*   **Tareas Típicas:**
    *   Crear/modificar/eliminar usuarios en el servidor RADIUS.
    *   Configurar VLANs, perfiles de tráfico y `service-ports` en las OLTs.
    *   Enviar comandos de desconexión (CoA - Change of Authorization) a través de RADIUS.
    *   Ejecutar playbooks de Ansible para configuraciones complejas.

### 2.2. Conectores y Controladores

*   **SSH/Telnet:** Para interactuar con equipos que no disponen de una API moderna (e.g., OLTs, switches). Se utilizan librerías como Paramiko o Netmiko para ejecutar comandos de forma segura.
*   **API REST:** Para la integración con equipos y sistemas que exponen una API (e.g., algunos modelos de routers, sistemas de monitoreo).
*   **Pyrad (RADIUS):** Se utiliza la librería `pyrad` para construir y enviar paquetes RADIUS para la gestión de NAS (Network Access Server) y la autenticación de usuarios (AAA).

### 2.3. Wizards de Odoo

*   **`isp_netdev_radius_client_wizard.py`:** Un asistente en la interfaz de Odoo para agregar manualmente un cliente RADIUS.
*   **`isp_radius_disconnect_wizard.py`:** Un asistente para disparar manualmente una desconexión de un cliente a través de un CoA.

## 3. Flujos de Trabajo Críticos

1.  **Activación de un Nuevo Servicio:**
    *   **Disparador:** El estado del `isp.contract` cambia a "Activo".
    *   **Acciones:**
        1.  Se encola una tarea de aprovisionamiento.
        2.  El worker toma la tarea y lee los datos del contrato (cliente, plan, IP, etc.).
        3.  Se crea el usuario en el servidor **RADIUS** con el perfil de velocidad correspondiente al plan.
        4.  Se establece una conexión **SSH/API** con la **OLT** correspondiente.
        5.  Se configura el `service-port`, las VLANs y los perfiles de tráfico para la ONU del cliente.
        6.  Se actualiza el contrato en Odoo con un log de la operación.

2.  **Suspensión por Morosidad:**
    *   **Disparador:** El estado del `isp.contract` cambia a "Suspendido".
    *   **Acciones:**
        1.  Se encola una tarea de suspensión.
        2.  El worker envía un comando **CoA-Disconnect** al servidor RADIUS para interrumpir la sesión del cliente.
        3.  Opcionalmente, se marca el puerto del contrato con el flag `is_cutoff_port` o se modifica la configuración en la OLT para cortar el servicio.

3.  **Cambio de Plan:**
    *   **Disparador:** El `product_id` en el `isp.contract` es modificado.
    *   **Acciones:**
        1.  Se encola una tarea de modificación.
        2.  El worker actualiza el perfil del usuario en **RADIUS** para reflejar la nueva velocidad.
        3.  Se envía un comando **CoA-Request** para que el cambio se aplique sin necesidad de que el cliente se reconecte.

## 4. Integraciones

*   **`silver_contract`:** Es el principal disparador de los flujos de aprovisionamiento.
*   **`silver_isp`:** Proporciona la información de los equipos de red (`isp.netdev`, `isp.olt`) a los que `silver_provisioning` debe conectarse, incluyendo IPs y credenciales.
*   **Servidor RADIUS (externo):** Sistema de Autenticación, Autorización y Contabilidad (AAA).
*   **Equipos de Red (externos):** OLTs, Routers, Switches.

## 5. Seguridad y Fiabilidad

*   **Gestión de Secretos:** Las credenciales para acceder a los equipos de red no deben estar en el código. Se recomienda el uso de un sistema como **HashiCorp Vault** o variables de entorno seguras.
*   **Idempotencia:** Las operaciones deben ser idempotentes, lo que significa que ejecutar la misma tarea varias veces no debe producir resultados no deseados.
*   **Manejo de Errores y Reintentos:** Las tareas deben implementar una política de reintentos exponenciales en caso de fallo de comunicación. Los fallos persistentes deben ser registrados en una "dead-letter queue" para revisión manual.
*   **Auditoría:** Todas las operaciones ejecutadas en los equipos de red deben quedar registradas en un log (`exec_log`) asociado al contrato o al equipo.
