/** @odoo-module **/

//import fieldRegistry from 'web.field_registry';
import { registry } from "@web/core/registry";
import basicFields from 'web.basic_fields';

const IPAddressWidget = basicFields.FieldChar.extend({
    widget_type: 'ip_address', // Un identificador único para tu widget

    // Método para validar el formato de la IP
    _isValidIP(ip) {
        if (!ip) return true; // Permite campos vacíos
        const ipFormat = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return ipFormat.test(ip);
    },

    // Sobrescribe el método de validación del campo
    _validateValue: function(value) {
        // Llama primero a la validación padre (si hay alguna)
        const parentValidation = this._super.apply(this, arguments);
        if (parentValidation !== true) {
            return parentValidation; // Si la validación padre falla, devuelve el error
        }

        if (!this._isValidIP(value)) {
            return "Debe ser una dirección IP válida (ej. 192.168.1.1).";
        }
        return true; // Todo correcto
    },

    // Opcional: Puedes añadir feedback visual o en el input
    // Por ejemplo, para destacar el input si hay un error
    // El _renderReadonly, _renderEdit, etc., son métodos para controlar la UI
});

// Registra tu widget en el registro de campos de Odoo
registry.add('ip_address', IPAddressWidget);

export default IPAddressWidget;
