/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Chatter } from "@mail/chatter/web_portal/chatter";
import { session } from "@web/session";
import { useRef, useEffect } from "@odoo/owl";

patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
        const model = this.props.threadModel || 'default';
        const collapseKey = `chatter_collapsed_${session.uid}_${model}`;
        this.state.isCollapsed = window.localStorage.getItem(collapseKey) === 'true';
        this.root = useRef("root");
        
        useEffect(() => {
            const el = this.root && this.root.el;
            if (el) {
                // Use setTimeout to ensure the container is fully rendered and accessible in the DOM hierarchy
                setTimeout(() => {
                    const container = el.closest('.o-mail-Form-chatter') || el.closest('.o-mail-ChatterContainer');
                    if (container) {
                        if (this.state.isCollapsed) {
                            container.classList.add('o-chatter-collapsed-container');
                        } else {
                            container.classList.remove('o-chatter-collapsed-container');
                        }
                    }
                }, 0);
            }
        }, () => [this.state.isCollapsed, this.state.thread, this.root.el]);
    },

    get isSendMessageHidden() {
        if (!this.props.threadModel) {
            return false;
        }
        const hiddenModels = session.chatter_hidden_models || [];
        return hiddenModels.includes(this.props.threadModel);
    },

    get isCollapseEnabled() {
        if (!this.props.threadModel) {
            return false;
        }
        const collapsibleModels = session.chatter_collapsible_models || [];
        return collapsibleModels.includes(this.props.threadModel);
    },

    toggleChatterCollapse() {
        this.state.isCollapsed = !this.state.isCollapsed;
        const model = this.props.threadModel || 'default';
        const collapseKey = `chatter_collapsed_${session.uid}_${model}`;
        window.localStorage.setItem(collapseKey, this.state.isCollapsed);
    }
});
