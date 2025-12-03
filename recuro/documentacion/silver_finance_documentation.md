# Documentación del Módulo: silver_collections y Finanzas

## 1. Visión General y Estratégica

**`silver_collections`** es el módulo encargado de la gestión de cobros y pasarelas de pago. En un ISP con miles de suscriptores, la conciliación manual de transferencias bancarias es inviable. Este módulo busca automatizar la recepción de pagos y su imputación a las facturas correspondientes.

Su filosofía es **"Agnóstico al Proveedor"**: Define una estructura común para transacciones de pago, permitiendo conectar múltiples bancos o pasarelas (Banesco, Pago Móvil, Zelle, Stripe) mediante conectores específicos.

### 1.1. Objetivos de Negocio

*   **Conciliación Automática:** Detectar un pago entrante y cruzarlo con el contrato del cliente automáticamente.
*   **Autogestión:** Permitir que el cliente reporte su pago a través del portal, reduciendo la carga administrativa.
*   **Reducción de la Morosidad:** Agilizar el proceso de reactivación de servicio al confirmar el pago en tiempo real.

## 2. Modelos de Datos Principales

### 2.1. `payment.transaction` (Transacción de Pago)
Es el registro maestro de un intento de pago.
*   **Campos:**
    *   `reference`: ID único de la transacción en Odoo.
    *   `provider_reference`: ID devuelto por el banco/pasarela (ej. número de referencia bancaria).
    *   `amount`: Monto pagado.
    *   `contract_id`: Contrato al que se aplica el pago.
    *   `state`: `Draft` -> `Pending` -> `Done` (Conciliado) / `Failed`.
    *   `raw_request/response`: Logs técnicos de la comunicación con la API del banco (crucial para auditoría).

### 2.2. `payment.provider` (Proveedor de Pago)
Configuración de la pasarela.
*   Credenciales API (Token, Usuario, Clave).
*   Métodos soportados (Tarjeta, Transferencia, Pago Móvil).
*   Estado (Test/Producción).

## 3. Flujos de Trabajo

### 3.1. Reporte de Pago (Manual o Portal)
1.  El cliente realiza una transferencia.
2.  Ingresa al portal o envía el comprobante.
3.  Se crea un `payment.transaction` en estado `Pending`.
4.  El sistema (o un operador) valida la referencia contra el banco.
5.  Si es válida, la transacción pasa a `Done`.

### 3.2. Conciliación (Payment Matching)
Cuando una transacción pasa a `Done`:
1.  Se genera automáticamente un `account.payment` (Pago contable) en Odoo.
2.  Se busca la factura abierta (`account.move`) más antigua del contrato asociado.
3.  Se "concilia" (cruza) el pago con la factura, marcándola como "Pagada".
4.  Si el contrato estaba suspendido, esto dispara la reactivación automática (ver `silver_contract`).

## 4. Instalación y Dependencias

*   **Dependencias:**
    *   `silver_contract` (Para asociar pagos a contratos).
    *   `silver_accounting` (Si existe, para lógica contable extra).
    *   `account` (Módulo base de contabilidad).
