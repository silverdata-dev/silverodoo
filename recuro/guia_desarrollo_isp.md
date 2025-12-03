# Guía de Desarrollo Odoo para un ISP en Venezuela (Explicado para Devs)

## Introducción: No le temas a la Contabilidad

Este documento es tu mapa. La contabilidad parece un monstruo de otro planeta, pero para un desarrollador, no es más que un sistema de CRUDs con reglas de negocio muy estrictas. El objetivo aquí es traducir los procesos de un ISP en Venezuela a los modelos de Odoo con los que vas a interactuar y, lo más importante, identificar **dónde y qué necesitas desarrollar**.

---

### Parte 1: Contabilidad para Dummies (¡Y para Devs!) - Los 3 Modelos que Gobiernan Todo

Antes de tocar una línea de código, olvida todo y piensa en la contabilidad como un gran libro de registros. En Odoo, este "libro" se representa principalmente con 3 modelos:

1.  **El Plan de Cuentas (`account.account`)**:
    *   **¿Qué es?** Es el "índice" de tu libro contable. Una lista de todas las categorías donde el dinero puede entrar o salir.
    *   **Ejemplos sencillos:** "110101 - Caja Principal", "110102 - Banco Mercantil", "410101 - Ventas de Internet Residencial", "610101 - Gastos de Electricidad".
    *   **Tu Rol como Dev:** Casi nunca crearás estas cuentas. El contador las define. Tú solo las usarás para decirle a Odoo "dónde" registrar el dinero.

2.  **Los Diarios (`account.journal`)**:
    *   **¿Qué es?** Son los "capítulos" o "carpetas" de tu libro. Agrupan transacciones del mismo tipo.
    *   **Ejemplos:** Un diario de "Ventas" (para todas las facturas a clientes), un diario de "Banco Mercantil" (para todos los pagos que entran y salen de esa cuenta), un diario de "Compras" (para facturas de proveedores).
    *   **Tu Rol como Dev:** El contador los configura. Tú los usarás para indicar en qué "capítulo" del libro debe guardarse una transacción. Por ejemplo, una factura de venta siempre irá al diario de ventas.

3.  **El Asiento Contable (`account.move`) y sus Líneas (`account.move.line`)**:
    *   **¿Qué es `account.move`?** ¡Esta es la clave de todo! Es una "página" en tu libro contable. Una factura es un `account.move`. Un pago es un `account.move`. Un gasto es un `account.move`. Es el registro de una transacción.
    *   **¿Qué es `account.move.line`?** Son las "líneas" escritas en esa página. Cada asiento (`account.move`) tiene al menos dos líneas.
    *   **La Regla de Oro (Partida Doble):** Por cada transacción, el total de los "débitos" debe ser igual al total de los "créditos". No te compliques con los términos. Piénsalo así:
        *   **Débito:** A dónde *va* el valor.
        *   **Crédito:** De dónde *sale* el valor.
        *   **Ejemplo simple:** Vendes un plan de internet por $10 y te pagan en efectivo.
            *   Se crea un `account.move` (el asiento).
            *   Línea 1 (`account.move.line`): **Débito** de $10 a la cuenta "Caja" (`account.account`). El dinero *fue a* la caja.
            *   Línea 2 (`account.move.line`): **Crédito** de $10 a la cuenta "Ventas de Internet" (`account.account`). El valor *salió de* un servicio que vendiste.
            *   El asiento está "cuadrado" ($10 = $10). ¡Listo!
    *   **Tu Rol como Dev:** **Este es tu campo de juego.** Gran parte de tu trabajo será crear o modificar registros `account.move` y sus `account.move.line` de forma programática.

---

### Parte 2: El Ciclo de Vida de un Cliente ISP en Odoo (El "Pasito a Pasito" con Modelos)

Aquí mapeamos el proceso de negocio a los modelos que acabas de aprender.

#### **Paso 1: Contratación e Instalación del Servicio**

*   **Proceso del Mundo Real:** Un cliente llama, pide un plan de 100 Mbps. Se le aprueba y un técnico va a instalarle un router.
*   **Mapeo en Odoo:**
    1.  **Presupuesto/Pedido de Venta (`sale.order`):** Se crea un pedido de venta para el cliente con el plan y el costo de instalación.
    2.  **Guía de Despacho (`stock.picking`):** Desde el `sale.order`, se genera una orden de almacén para darle salida al router que se le va a instalar. El módulo `l10n_ve_stock_account` es clave aquí, porque este `stock.picking` representa la "Nota de Entrega".
    3.  **Activo Fijo (`account.asset`):** Si el router no se le vende al cliente sino que se le da en comodato, se puede registrar como un activo de la empresa usando `account_asset_management`.

*   **¿Qué tienes que desarrollar aquí?**
    *   **Poco o nada.** Este flujo es bastante estándar. Tu principal tarea podría ser **personalizar el formato PDF de la Nota de Entrega** para que cumpla con los requisitos de la empresa, usando QWeb.

#### **Paso 2: La Facturación Mensual Automática**

*   **Proceso del Mundo Real:** El día 1 de cada mes, hay que generar miles de facturas para todos los clientes activos.
*   **Mapeo en Odoo:**
    1.  **Plantilla Recurrente (`recurring.template` del módulo `om_recurring_payments`):** Por cada cliente, se crea una plantilla que dice: "A este cliente, cada mes, genérale una factura con este plan y este precio".
    2.  **Cron Job:** Un proceso automático (cron) corre periódicamente (ej. cada día) y busca qué plantillas deben ejecutarse.
    3.  **Creación de Factura (`account.move`):** El cron, usando la plantilla, crea un nuevo `account.move` de tipo `out_invoice` (Factura de Cliente).
    4.  **Tasa de Cambio (`res.currency.rate`):** Al momento de crear la factura, el sistema consulta la tasa del día (gracias a `l10n_ve_currency_rate_live`) para calcular el monto en Bolívares si la tarifa está en Dólares.
    5.  **Número de Control (`l10n_ve_invoice`):** Al validar la factura (`action_post`), el módulo de localización le asigna un número de control único desde la secuencia del diario (`account.journal`).

*   **¿Qué tienes que desarrollar aquí?**
    *   **Casi nada en la lógica principal.** El trabajo es de **configuración**.
    *   **Tarea de Desarrollo:** **Personalizar el formato de la factura (PDF)** para que sea compatible con la impresora fiscal o cumpla con los requisitos del SENIAT. Esto se hace modificando la vista QWeb `report_invoice_document`.

#### **Paso 3: El Cliente Realiza un Pago**

*   **Proceso del Mundo Real:** El cliente paga por Pago Móvil o transferencia y reporta el pago.
*   **Mapeo en Odoo:**
    1.  **Registro del Pago (`account.payment`):** Se crea un registro de pago, especificando el cliente, el monto, el diario del banco receptor y la referencia del pago.
    2.  **Validación de Referencia (`l10n_ve_ref_bank`):** Al intentar validar el pago, este módulo puede verificar que la referencia no esté duplicada.
    3.  **Cálculo de IGTF (`l10n_ve_igtf`):** **¡Punto Crítico!** Si el diario del banco receptor está marcado como que "Aplica IGTF" (ej. una cuenta en divisas), este módulo se activa. Al validar el pago, crea un **segundo asiento contable (`account.move`)** por el 3% del monto, registrando el gasto de IGTF.
    4.  **Conciliación:** El pago se asocia a la factura (`account.move`) correspondiente, dejándola en estado "Pagado".

*   **¿Qué tienes que desarrollar aquí?**
    *   **Tarea Principal: Integración con Pasarelas de Pago.** El proceso manual de registrar pagos es lento. Tu tarea más importante será crear un módulo (ej. `silver_payment_gateway`) que:
        *   Exponga un endpoint (API) para que tu portal de clientes o pasarelas de pago (ej. Mercantil, Pago Rápido) notifiquen un pago.
        *   Al recibir una notificación, cree automáticamente el registro `account.payment` en Odoo y intente conciliarlo con la factura del cliente.

#### **Paso 4: El Contador Cierra el Mes**

*   **Proceso del Mundo Real:** El contador necesita generar el Libro de Ventas, el Libro de Compras y declarar las retenciones.
*   **Mapeo en Odoo:**
    1.  **Libros de IVA (`accounting_pdf_reports`):** El contador usa los asistentes de este módulo para generar los reportes de "Libro de Ventas" y "Libro de Compras" en PDF o Excel.
    2.  **Declaración de Retenciones (`l10n_ve_payment_extension`):** El contador va al módulo de retenciones, agrupa todas las retenciones del período y genera el archivo TXT para el portal del SENIAT.
    3.  **Conciliación Bancaria (`account.bank.statement`):** El contador carga el estado de cuenta del banco y lo compara con los pagos registrados en el sistema para asegurarse de que todo cuadre.

*   **¿Qué tienes que desarrollar aquí?**
    *   **Tarea Principal: Personalización de Reportes a la Medida.** Los módulos base generan los datos, pero es casi seguro que el formato del "Libro de Ventas" o "Libro de Compras" en Excel no será *exactamente* como lo quiere el contador o como lo exige una fiscalización.
    *   Deberás crear un módulo (ej. `silver_accounting_reports`) que herede de los asistentes de `accounting_pdf_reports` y, usando la librería `report_xlsx`, modifique las columnas, los formatos y los totales de los archivos Excel generados.

---

### Parte 3: Resumen de Tareas de Desarrollo Priorizadas

1.  **Integración de Pasarelas de Pago (Prioridad Alta):**
    *   **Módulo a crear:** `silver_payment_gateway`.
    *   **Objetivo:** Automatizar la creación de `account.payment` a partir de notificaciones de bancos o portales de pago. Esto reduce la carga operativa drásticamente.

2.  **Personalización de Documentos PDF (Prioridad Alta):**
    *   **Módulos a modificar (heredando):** `l10n_ve_invoice`, `l10n_ve_stock_account`, `l10n_ve_payment_extension`.
    *   **Objetivo:** Ajustar los PDFs de Facturas, Notas de Entrega y Comprobantes de Retención al formato exacto requerido. Implica trabajar con QWeb.

3.  **Personalización de Reportes Fiscales (Prioridad Media):**
    *   **Módulo a crear:** `silver_accounting_reports`.
    *   **Objetivo:** Generar el Libro de Ventas y Compras en formato XLSX exactamente como lo requiere el departamento de contabilidad. Implica usar la librería `report_xlsx_helper`.

4.  **Módulo de Contratos y Equipos (Prioridad Media - Mejora Estratégica):**
    *   **Módulo a crear:** `silver_isp_management`.
    *   **Objetivo:** Crear una entidad `isp.contract` que almacene el plan del cliente, la fecha de inicio, y el estado del servicio (Activo, Cortado). También un modelo `isp.equipment` para registrar el serial y MAC del equipo instalado en casa del cliente, vinculado al contrato.
    *   **Relaciones:** `res.partner` (1) -> (M) `isp.contract` (1) -> (M) `isp.equipment`. El contrato también se relacionaría con la plantilla de facturación recurrente.
    *   **Beneficio:** Esto centraliza la información del cliente y permite futuras automatizaciones (como cortes automáticos por falta de pago).

Con esta guía, tienes un camino claro. Empieza por familiarizarte con los modelos `account.move` y `account.payment`, ya que son el centro de casi toda la operación. Luego, aborda las tareas en el orden de prioridad sugerido. ¡Éxito!