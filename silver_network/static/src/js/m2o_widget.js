/** @odoo-module **/

import { Many2OneField } from "@web/views/fields/many2one/many2one_field";

import { registry } from "@web/core/registry";
//import fieldRegistry from 'web.field_registry';
//import { browser } from "@web/core/browser/browser";
//import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class MyDynamicMany2one extends Many2OneField {
    // Sobrescribimos el método que maneja el clic en el enlace
    async _onOpenRecord(ev) {
        ev.preventDefault(); // Evita el comportamiento por defecto

        const genericRecordId = this.value;
        if (!genericRecordId) {
            return;
        }

        alert ("hola1");
        // Acceder a la información del modelo a través del servidor
        // Hacemos una llamada al servidor para obtener el nombre del modelo
        const realModelName = await this.orm.call(
            "silver.netdev",
            "get_real_model_name_by_id", // Un método Python que debes crear
            [genericRecordId]
        );

        alert ("hola2");

        if (realModelName) {
            // Abre el formulario del modelo específico
            this.action.doAction({
                type: 'ir.actions.act_window',
                res_model: realModelName,
                res_id: genericRecordId,
                views: [[false, 'form']],
                target: 'new',
            });
        }
        alert ("hola3");
    }
}

// Registra tu nuevo widget
registry.category("fields").add("my_dynamic_m2o", MyDynamicMany2one);