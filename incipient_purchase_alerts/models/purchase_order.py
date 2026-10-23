from markupsafe import Markup
from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.state in ('purchase', 'done') and order.company_id.enable_po_price_increase_alert:
                order._check_price_increase_alerts()
        return res

    def _check_price_increase_alerts(self):
        for order in self:
            company = order.company_id
            recipients = company.po_price_increase_alert_user_ids
            price_increases = []

            for line in order.order_line:
                prev_line = self.env['purchase.order.line'].search([
                    ('order_id.partner_id', '=', order.partner_id.id),
                    ('product_id', '=', line.product_id.id),
                    ('order_id.state', 'in', ['purchase', 'done']),
                    ('order_id.id', '!=', order.id)
                ], order='id desc', limit=1)

                if prev_line and line.price_unit > prev_line.price_unit:
                    diff = line.price_unit - prev_line.price_unit
                    pct = (diff / prev_line.price_unit) * 100 if prev_line.price_unit > 0 else 100.0
                    price_increases.append(
                        Markup(_("• <b>%s</b>: Unit price increased from <b>%s</b> to <b>%s</b> (+%.2f%% / diff: %s)")) % (
                            line.product_id.display_name, prev_line.price_unit, line.price_unit, pct, diff
                        )
                    )

            if price_increases:
                body = Markup(_(
                    "<b>Price Increase Alert</b><br/>"
                    "Confirmed Purchase Order <b>%s</b> for vendor <b>%s</b> contains price increases over previous purchases:<br/><br/>%s"
                )) % (order.name, order.partner_id.display_name, Markup("<br/>").join(price_increases))

                all_recipients = recipients | order.user_id
                email_to = ','.join(filter(None, all_recipients.mapped('email')))
                if email_to:
                    order.env['mail.mail'].sudo().create({
                        'subject': f"Price Increase Alert: {order.name}",
                        'body_html': body,
                        'email_to': email_to,
                        'model': 'purchase.order',
                        'res_id': order.id,
                        'message_type': 'notification',
                        'author_id': order.env.user.partner_id.id,
                    })

                # Log note in chatter
                order.message_post(
                    body=body,
                    subject=f"Price Increase Alert: {order.name}",
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )
