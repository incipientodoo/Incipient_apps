from odoo import models

class AccountMoveSend(models.AbstractModel):
    _inherit = 'account.move.send'

    def _get_default_mail_partner_ids(self, move, mail_template, mail_lang):
        """
        Override:
        If the invoice's commercial entity has a primary accounting contact,
        use it as the default mail recipient.
        """
        partners = super()._get_default_mail_partner_ids(move, mail_template, mail_lang)
        
        commercial_partner = move.partner_id.commercial_partner_id
        if commercial_partner and commercial_partner.primary_account_partner_id:
            primary_partner = commercial_partner.primary_account_partner_id
            if primary_partner and primary_partner.email:
                # Replace the original invoice partner with the primary accounting partner
                partners = (partners - move.partner_id - commercial_partner) | primary_partner
            elif move.partner_id == primary_partner and not primary_partner.email:
                # If the primary partner has no email, fallback to the main contact
                if commercial_partner and commercial_partner.email:
                    partners = (partners - move.partner_id) | commercial_partner

        return partners
