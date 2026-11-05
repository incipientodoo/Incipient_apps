/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { messageActionsRegistry } from "@mail/core/common/message_actions";
import { toRaw } from "@odoo/owl";

messageActionsRegistry.add("reply-all", {
    condition: ({ message: msg, thread: thr }) => {
        const message = toRaw(msg);
        const thread = toRaw(thr);
        return (
            !["discuss.channel", "mail.box"].includes(thread?.model)
        );
    },
    icon: "fa fa-reply-all",
    name: _t("Reply All"),
    onSelected: ({ message: msg, owner, thread: thr }) => {
        const message = toRaw(msg);
        const thread = toRaw(thr);
        const composer = thread.composer;
        if (message.eq(composer.replyToMessage)) {
            composer.replyToMessage = undefined;
            return;
        }
        if (message.model !== "discuss.channel") {
            composer.insertReplyAllFromNote(message);
        }
        owner.env.inChatter?.toggleComposer("note", { force: true });
        composer.restoredFromFullComposer = false;
        if (!composer.isFocused) {
            composer.autofocus++;
        }
    },
    sequence: 71,
}, { force: true });
