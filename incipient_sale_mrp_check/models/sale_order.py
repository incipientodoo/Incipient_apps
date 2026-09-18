# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            missing_bom_products = []
            missing_operations_products = []
            missing_attachments_products = []
            
            for line in order.order_line:
                product = line.product_id
                if not product:
                    continue

                bom = self.env['mrp.bom']._bom_find(
                    products=product
                )

                if not bom:
                    missing_bom_products.append(product.display_name)
                    continue

                if not product.bom_ids.operation_ids:
                    missing_operations_products.append(product.display_name)
                    
                product_attach_count = product.message_attachment_count
                bom_attach_count = 0
                operation_attach_count = 0
                
                for bom_record in product.bom_ids:
                    bom_attach_count += bom_record.message_attachment_count
                    for operation in bom_record.operation_ids:
                        operation_attach_count += operation.message_attachment_count
                        
                if product_attach_count == 0 and bom_attach_count == 0 and operation_attach_count == 0:
                    missing_attachments_products.append(product.display_name)

            if missing_bom_products or missing_operations_products or missing_attachments_products:
                message = ""

                if missing_bom_products:
                    message += _(
                        "Bill of Material not found for the following products:\n• %s\n\n"
                    ) % "\n• ".join(sorted(set(missing_bom_products)))

                if missing_operations_products:
                    message += _(
                        "Bill of Material exists but no Operations are defined for the following products:\n• %s\n\n"
                    ) % "\n• ".join(sorted(set(missing_operations_products)))

                if missing_attachments_products:
                    message += _(
                        "No attachments found on Product / BoM / Operations for the following products:\n• %s\n\n"
                    ) % "\n• ".join(sorted(set(missing_attachments_products)))

                self._send_engineering_alert(
                    missing_bom_products,
                    missing_operations_products,
                    missing_attachments_products
                )

                raise ValidationError(message.strip())

        return super(SaleOrder, self).action_confirm()

    def _send_engineering_alert(self, missing_bom_products, missing_operations_products, missing_attachments_products):
        # FIXME: Client requested this alert temporary
        # return
        
        engineering_group = self.env.ref('incipient_sale_mrp_check.group_engineering_team', raise_if_not_found=False)
        if not engineering_group:
            return
            
        users = engineering_group.user_ids.filtered(lambda u: u.email)
        if not users:
            return

        email_to = ",".join(users.mapped('email'))
        body = "<p>The following issues were detected during Sale Order confirmation:</p>"

        if missing_bom_products:
            body += """
                <p><strong>Bill of Material not found for the following products:</strong></p>
                <ul>%s</ul>
            """ % "".join(f"<li>{p}</li>" for p in sorted(set(missing_bom_products)))

        if missing_operations_products:
            body += """
                <p><strong>Bill of Material exists but no Operations are defined for the following products:</strong></p>
                <ul>%s</ul>
            """ % "".join(f"<li>{p}</li>" for p in sorted(set(missing_operations_products)))

        if missing_attachments_products:
            body += """
                <p><strong>No attachments found on Product / BoM / Operations for the following products:</strong></p>
                <ul>%s</ul>
            """ % "".join(f"<li>{p}</li>" for p in sorted(set(missing_attachments_products)))

        self.env['mail.mail'].sudo().create({
            'subject': 'Engineering Alert: Missing BoM / Operations / Attachments',
            'body_html': body,
            'email_to': email_to,
        }).send()
