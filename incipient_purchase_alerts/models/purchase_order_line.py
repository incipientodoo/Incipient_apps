from markupsafe import Markup
from odoo import api, fields, models, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def write(self, vals):
        check_change = ('product_qty' in vals or 'price_unit' in vals)
        old_vals = {}
        if check_change:
            for line in self:
                old_vals[line.id] = {
                    'qty': line.product_qty,
                    'price': line.price_unit,
                }

        res = super().write(vals)

        if check_change:
            for line in self:
                if line.order_id.state in ('purchase', 'done') and line.order_id.company_id.enable_po_change_alert:
                    old = old_vals.get(line.id, {})
                    changes = []
                    if 'product_qty' in vals and old.get('qty') != line.product_qty:
                        changes.append(Markup(_("Quantity changed from <b>%s</b> to <b>%s</b>")) % (old.get('qty'), line.product_qty))
                    if 'price_unit' in vals and old.get('price') != line.price_unit:
                        changes.append(Markup(_("Unit Price changed from <b>%s</b> to <b>%s</b>")) % (old.get('price'), line.price_unit))
                    
                    if changes:
                        company = line.order_id.company_id
                        recipients = company.po_change_alert_user_ids
                        body = Markup(_(
                            "<b>PO Line Modification Alert</b><br/>"
                            "Purchase Order <b>%s</b> line for product <b>%s</b> was modified:<br/>%s"
                        )) % (line.order_id.name, line.product_id.display_name, Markup("<br/>").join(changes))

                        email_to = ','.join(filter(None, recipients.mapped('email')))
                        if email_to:
                            line.env['mail.mail'].sudo().create({
                                'subject': f"PO Modified: {line.order_id.name}",
                                'body_html': body,
                                'email_to': email_to,
                                'model': 'purchase.order',
                                'res_id': line.order_id.id,
                                'message_type': 'notification',
                                'author_id': line.env.user.partner_id.id,
                            })
                            
                        # Log note in chatter
                        line.order_id.message_post(
                            body=body,
                            subject=f"PO Modified: {line.order_id.name}",
                            message_type='notification',
                            subtype_xmlid='mail.mt_note'
                        )

        return res
