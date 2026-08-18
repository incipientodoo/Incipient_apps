from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_credit_hold = fields.Boolean(
        string='Credit Hold',
        default=False,
        copy=False,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if order.state in ('draft', 'sent'):
                order._check_credit_limit()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get('skip_credit_check'):
            return res
        if any(k in vals for k in ['order_line', 'partner_id']):
            for order in self:
                if order.state in ('draft', 'sent'):
                    order._check_credit_limit()
        return res

    def _check_credit_limit(self):
        for order in self:
            # Check Past Due Balance
            total_overdue = order.partner_id.total_overdue if hasattr(order.partner_id, 'total_overdue') else 0.0
            if total_overdue > 0:
                order._move_to_credit_hold(reason_type="Past Due")
                continue

            # Check Credit Limit
            credit_limit = order.partner_id.credit_limit
            if not credit_limit:
                continue
            other_orders = self.env['sale.order'].search([
                ('partner_id', '=', order.partner_id.id),
                ('state', 'in', ['draft', 'sent']),
                ('id', '!=', order.id),
                ('is_credit_hold', '=', False),
            ])
            total_amount = sum(other_orders.mapped('amount_total')) + order.amount_total
            if total_amount > credit_limit:
                order._move_to_credit_hold(reason_type="Credit Limit")

    def _move_to_credit_hold(self, reason_type="Credit Limit"):
        for order in self:
            if order.is_credit_hold:
                continue
            order.with_context(skip_credit_check=True).write({'is_credit_hold': True})
            order._send_credit_hold_notification()
            
            if reason_type == "Credit Limit":
                msg = _(
                    "⚠️ Credit limit exceeded.\n"
                    "Credit Limit: %.2f\n"
                    "Order Amount: %.2f"
                ) % (order.partner_id.credit_limit, order.amount_total)
            else:
                msg = _(
                    "⚠️ Customer has past due balance.\n"
                    "Past Due Amount: %.2f"
                ) % (order.partner_id.total_overdue if hasattr(order.partner_id, 'total_overdue') else 0.0)
                
            order.message_post(body=msg)

    def action_release_credit_hold(self):
        self.ensure_one()
        return {
            'name': _('Release Credit Hold'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.credit.release',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def action_confirm(self):
        for order in self:
            if order.is_credit_hold:
                raise UserError(_("You cannot confirm an order that is on Credit Hold. Please have the accounting team release the hold first."))
        return super().action_confirm()

    def _send_credit_hold_notification(self):
        template = self.env.ref(
            'sale_credit_hold.mail_template_credit_hold_notification',
            raise_if_not_found=False,
        )
        if template:
            template.send_mail(self.id, force_send=True)