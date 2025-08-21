/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";
import { AssetMapView } from "./map_view";


export class NodeMapWidget extends Component {
    static components = { AssetMapView };
    static template = "silver_isp.NodeMapWidget";
    static props = {
        ...standardFieldProps,
        nodeId: {
            type: String,
            optional: true
        },
        action: {
            optional: true,
        },
        className: {
            optional: true,
        }

    
        }    ;

    get nodeId() {
        return this.props.record.resId;
    }
}

registry.category("fields").add("node_map", {
    component:NodeMapWidget 
}
);
