from odoo import models, fields, api, _
from odoo.tools import float_round

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        [
            ('draft', "Quote"),
            ('waiting_for_approval','Waiting for Approval'),
            ('denied','Denied'),
            ('approved','Approved'),
            ('approved_to_send','Approved to Send'),
            ('sent', "Quote Sent"),
            ('rejected','Rejected'),
            ('accepted','Accepted'),
            ('waiting_for_acceptance', "Waiting for Acceptance"),
            ('ready_schedule', "Ready To Schedule"),
            ('sale', "Sales Order"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        tracking=3,
        default='draft'
    )

    extra_discount = fields.Float(string="Total Additional Discount", compute="_compute_extra_discount", store=True)

    show_send_for_approval = fields.Boolean(
        string="Show Send For Approval",
        compute='_compute_button_visibility'
    )
    show_send_to_customer = fields.Boolean(
        string="Show Send To Customer",
        compute='_compute_button_visibility'
    )
    is_payment_term_readonly = fields.Boolean(
        compute='_compute_is_payment_term_readonly',
        store=False
    )
    is_send_to_customer = fields.Boolean(copy=False)

    sale_discount_total = fields.Float(
        string="Volume Discount",
        compute="_compute_sale_discount_total",
    )
    discount_total = fields.Float(
        string="Total Discount",
        compute="_compute_discount_total",
    )
    additional_discount_total = fields.Float(string="Additional Discount", compute="_compute_additional_discount_total")
    max_additional_discount = fields.Float(compute="_compute_max_additional_discount", store=True, default=0)

    def _compute_discount_total(self):
        for order in self:
            order.discount_total = sum(order.order_line.mapped("total_discount_amount"))

    @api.depends('order_line.additional_discount')
    def _compute_max_additional_discount(self):
        for order in self:
            order.max_additional_discount = order.order_line and max(
                order.order_line.mapped("additional_discount")) or 0.0

    def _compute_additional_discount_total(self):
        for order in self:
            order.additional_discount_total = sum(order.order_line.mapped("additional_discount_amount"))

    def _compute_sale_discount_total(self):
        for order in self:
            order.sale_discount_total = sum(order.order_line.mapped("sale_discount_amount"))

    @api.depends('order_line.additional_discount_amount', 'amount_undiscounted')
    def _compute_extra_discount(self):
        for rec in self:
            total_additional_discount_amount = sum(rec.order_line.mapped('additional_discount_amount'))
            rec.extra_discount = 0
            if total_additional_discount_amount:
                if rec.amount_undiscounted:
                    rec.extra_discount = total_additional_discount_amount / rec.amount_undiscounted

    def _confirmation_error_message(self):
        self.ensure_one()
        # Allow confirmation from ready_schedule
        if self.state not in {'draft', 'sent', 'ready_schedule'}:
            return _("Some orders are not in a state requiring confirmation.")
        if any(
                not line.display_type
                and not line.is_downpayment
                and not line.product_id
                for line in self.order_line
        ):
            return _("A line on these orders is missing a product, you cannot confirm it.")
        return False

    @api.depends('extra_discount', 'state')
    def _compute_button_visibility(self):
        for order in self:
            # extra_discount is a fraction (e.g. 0.15 for 15%)
            discount_percentage = float_round((order.extra_discount or 0.0) * 100, precision_digits=4)
            threshold = 5.0
            order.show_send_for_approval = order.state == 'draft' and discount_percentage > threshold
            order.show_send_to_customer = (order.state == 'draft' and discount_percentage <= threshold) or (order.state == 'approved_to_send')

    def _compute_is_payment_term_readonly(self):
        readonly_users = self.env.user.has_group(
            'incipient_so_approval_discount_customization.group_unex_payment_term'
        )
        for order in self:
            order.is_payment_term_readonly = readonly_users

    def action_approve(self):
        for order in self:
            order.state = 'approved'

    def action_denied(self):
        for order in self:
            order.state = 'denied'

    def action_approve_to_send(self):
        for order in self:
            order.state = 'approved_to_send'

    def action_send_for_approval(self):
        for order in self:
            order.state = 'waiting_for_approval'
            # order.locked = True # Note: locked is only available if sale_management is fully used with locks, commenting out if not present, but keeping as source had it. Wait, source had order.locked = True. Let's keep it.
            order.locked = True

    def action_accept(self):
        for order in self:
            if order.amount_total >= 25000:
                order.state = 'waiting_for_acceptance'
            else:
                order.state = 'accepted'

    def action_reject(self):
        for order in self:
            order.state = 'rejected'

    def action_send_to_customer(self):
        for order in self:
            days = order.company_id.quotation_validity_days or 0
            order.is_send_to_customer = True
            order.state = 'sent'
            # order.quotation_sent_date = fields.Date.context_today(order) or fields.Datetime.now().date()
            # order.validity_date = order.quotation_sent_date + timedelta(days=days)

    def action_accepted(self):
        for order in self:
            order.state = 'ready_schedule'

    def action_ready_for_schedule(self):
        for order in self:
            order.state = 'ready_schedule'
