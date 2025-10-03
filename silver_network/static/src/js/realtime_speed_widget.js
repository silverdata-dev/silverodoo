/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";

// This is a simple component that just displays the speed.
// The actual data fetching will be handled by the parent view.
export class RealtimeSpeedWidget extends CharField {}

RealtimeSpeedWidget.template = "web.CharField"; // Use a standard template

registry.category("fields").add("realtime_speed", {
    component: RealtimeSpeedWidget,
});
