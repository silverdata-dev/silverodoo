/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Many2OneField } from "@web/views/fields/many2one/many2one_field";
import { patch } from "@web/core/utils/patch";

/**
 * Extensión del Many2one para forzar la apertura del registro en un popup (modal).
 * Usamos la función de 'openRecord' y le pasamos el target 'new'.
 */
class Many2OneModalField extends Many2OneField {

    // Sobrescribimos el método original que se ejecuta al hacer clic en el nombre.
    openRecord(e) {
        // La función openRecord ya existe en el componente padre.
        // Lo crucial es el objeto de 'context' que le pasamos.

        // 1. Evitamos el comportamiento por defecto (que haría la navegación interna).
        if (e) {
            e.preventDefault();
        }

        // 2. Si hay un ID y tenemos permiso de edición (es decir, es un enlace válido)
        if (this.props.value && this.canOpen) {

            // Forzamos el target a 'new' (abre en modal/popup) y pasamos los props.
            this.props.openRecord({
                resId: this.props.value,
                resModel: this.props.relation,
                context: { 'target': 'new' } // <-- ¡El secreto está aquí!
            });
        }
    }
}

// Registramos el nuevo widget con un nombre fácil de usar en el XML.
Many2OneModalField.template = "web.Many2oneField"; // Usa la plantilla original
Many2OneModalField.components = Many2OneField.components;
Many2OneModalField.displayName = "Many2one Modal";

// Exportamos el widget.
export const myMany2oneModal = {
    ...Many2OneModalField,
    // La clave 'widget' que usarás en el XML
    extractProps: ({ attrs }) => {
        return {
            ...Many2OneField.extractProps({ attrs }),
            // Si necesitas lógica adicional
        };
    },
};

// Registramos el widget con el nombre que usarás en el XML
registry.category("fields").add("many2one_modal", myMany2oneModal);

console.log("holaaaa");
