/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { CharField } from "@web/views/fields/char/char_field";

export class RecordLink extends Component {
    setup() {
        this.action = useService("action");
    }

    get recordId() {
        return this.props.record.resId;
    }

    get recordModel() {
        return this.props.record.resModel;
    }

    get fieldValue() {
       // console.log(["fieldvalue", this.props.value, this.props, this, this.props.get("name")]);
        return this.props.record.data[this.props.name]  || "";
    }

    onClick(ev) {
        ev.preventDefault();
        console.log(["ev", ev, this.props]);
        if (this.props.record.data["id"] && this.props.record.evalContext['active_model']) {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: this.props.record.evalContext['active_model'],
                res_id: this.props.record.data["id"],
                views: [[false, "form"]],
                target: "current",
            });
        }
    }
}

RecordLink.template = "silver_base.RecordLink";
RecordLink.props = {
    ...CharField.props,
};

export const recordLink = {
    component: RecordLink,
    extractProps: ({ attrs }) => ({}),
};

registry.category("fields").add("record_link", recordLink);
