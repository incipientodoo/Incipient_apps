/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer_model";
import { generatePartnerMentionElement } from "@mail/utils/common/format";
import { createDocumentFragmentFromContent } from "@web/core/utils/html";
import { nbsp } from "@web/core/utils/strings";
import { markup } from "@odoo/owl";

patch(Composer.prototype, {
    /** @param {import("models").Message} message */
    insertReplyAllFromNote(message) {
        const partnersToMentionMap = new Map();
        if (this.thread && this.thread.messages) {
            for (const msg of this.thread.messages) {
                if (msg.author_id) {
                    partnersToMentionMap.set(msg.author_id.id, msg.author_id);
                }
                if (msg.partner_ids) {
                    for (const partner of msg.partner_ids) {
                        partnersToMentionMap.set(partner.id, partner);
                    }
                }
            }
        } else {
            if (message.author_id) {
                partnersToMentionMap.set(message.author_id.id, message.author_id);
            }
            if (message.partner_ids) {
                for (const partner of message.partner_ids) {
                    partnersToMentionMap.set(partner.id, partner);
                }
            }
        }
        const partnersToMention = Array.from(partnersToMentionMap.values()).filter(
            (partner) => !this.store.self || partner.id !== this.store.self.id
        );

        for (const partner of partnersToMention) {
            this.mentionedPartners.add(partner);
        }

        if (!this.store.env.services["mail.composer"].htmlEnabled) {
            for (const partner of partnersToMention) {
                const partnerName = this.thread?.getPersonaName(partner) || partner.displayName || partner.name || "Unnamed";
                const mentionText = `@${partnerName} `;
                if (!this.composerText.includes(mentionText)) {
                    this.insertText(mentionText, 0, { moveCursorToEnd: true });
                }
            }
            return;
        }

        const composerBody = createDocumentFragmentFromContent(this.composerHtml).body;
        // Mentions are inserted at the beginning, so we reverse the order to keep the original order
        const partnersList = [...partnersToMention].reverse();
        for (const partner of partnersList) {
            if (
                composerBody.querySelector(
                    `a.o_mail_redirect[data-oe-model="res.partner"][data-oe-id="${partner.id}"]`
                )
            ) {
                continue;
            }
            composerBody.firstElementChild.prepend(
                generatePartnerMentionElement(partner, this.thread),
                nbsp
            );
        }
        this.composerHtml = markup(composerBody.innerHTML);
    }
});
