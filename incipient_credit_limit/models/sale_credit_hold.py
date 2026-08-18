from odoo import models, fields, _


# class SaleCreditHold(models.Model):
#     _name = 'sale.credit.hold'
#     _description = 'Sale Credit Hold'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _order = 'create_date desc'
#
#     def action_release(self):
#         """
#         Releases the credit hold:
#         - Sets is_credit_hold = False on the sale order
#         - Posts a message on the sale order
#         - Deletes this credit hold record
#         """
#         for record in self:
#             record.sale_order_id.with_context(skip_credit_check=True).write({
#                 'is_credit_hold': False
#             })
#             record.sale_order_id.message_post(
#                 body=_("✅ Credit Hold released by %s. Moved back to Quotations.", self.env.user.name)
#             )
#             record.unlink()
#         return True