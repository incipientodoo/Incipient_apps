from markupsafe import Markup
from odoo import models, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.state == 'done' and picking.purchase_id:
                po = picking.purchase_id
                company = picking.company_id or po.company_id
                if company.enable_receipt_confirm_alert:
                    picking._send_receipt_confirmation_alert()
        return res

    def _send_receipt_confirmation_alert(self):
        self.ensure_one()
        po = self.purchase_id
        company = self.company_id or po.company_id
        recipients = company.receipt_confirm_alert_user_ids
        
        lines_summary = []
        for move in self.move_ids.filtered(lambda m: m.state == 'done'):
            lines_summary.append(f"• {move.product_id.display_name}: Received Qty {move.quantity} {move.product_uom.name}")
        
        body = Markup(_(
            "<b>Receipt Confirmation Alert</b><br/>"
            "Inventory receipt <b>%s</b> for Purchase Order <b>%s</b> (Vendor: %s) has been fully validated/received.<br/><br/>"
            "<b>Received Items:</b><br/>%s"
        )) % (self.name, po.name, po.partner_id.display_name, Markup("<br/>").join(lines_summary))

        email_to = ','.join(filter(None, recipients.mapped('email')))
        if email_to:
            self.env['mail.mail'].sudo().create({
                'subject': f"Receipt Confirmed: {po.name}",
                'body_html': body,
                'email_to': email_to,
                'model': 'purchase.order',
                'res_id': po.id,
                'message_type': 'notification',
                'author_id': self.env.user.partner_id.id,
            })
            
        # Log note in chatter
        po.message_post(
            body=body,
            subject=f"Receipt Confirmed: {po.name}",
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
