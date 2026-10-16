# -*- coding: utf-8 -*-
from markupsafe import Markup
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('waiting_approval', "Waiting Approval")],
        ondelete={'waiting_approval': 'set default'}
    )

    needs_customer_approval = fields.Boolean(
        string="Needs Customer Sign-Off",
        compute="_compute_approval_requirements",
        store=True,
        tracking=True
    )
    needs_manager_approval = fields.Boolean(
        string="Needs Manager Approval",
        compute="_compute_approval_requirements",
        store=True,
        tracking=True
    )

    customer_approval_state = fields.Selection([
        ('not_required', 'Not Required'),
        ('pending', 'Pending Sign-Off'),
        ('approved', 'Signed Off'),
        ('rejected', 'Rejected'),
    ], string="Customer Sign-Off Status", default='not_required', copy=False, tracking=True)

    customer_approval_date = fields.Datetime(
        string="Customer Sign-Off Date",
        readonly=True,
        copy=False
    )
    customer_approval_user_id = fields.Many2one(
        'res.users',
        string="Customer Sign-Off Recorded By",
        readonly=True,
        copy=False
    )

    manager_approval_state = fields.Selection([
        ('not_required', 'Not Required'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string="Manager Approval Status", default='not_required', copy=False, tracking=True)

    manager_approval_date = fields.Datetime(
        string="Manager Approval Date",
        readonly=True,
        copy=False
    )
    manager_approval_user_id = fields.Many2one(
        'res.users',
        string="Approved By Manager",
        readonly=True,
        copy=False
    )

    @api.depends('order_line.require_customer_approval', 'order_line.require_manager_approval')
    def _compute_approval_requirements(self):
        for order in self:
            requires_cust = any(line.require_customer_approval for line in order.order_line if not line.display_type)
            requires_mgr = any(line.require_manager_approval for line in order.order_line if not line.display_type)
            order.needs_customer_approval = requires_cust
            order.needs_manager_approval = requires_mgr

    def _confirmation_error_message(self):
        self.ensure_one()
        if self.state == 'waiting_approval':
            return False
        return super()._confirmation_error_message()

    def action_confirm(self):
        orders_to_hold = self.env['sale.order']
        for order in self:
            cust_needed = order.needs_customer_approval and order.customer_approval_state != 'approved'
            mgr_needed = order.needs_manager_approval and order.manager_approval_state != 'approved'

            if cust_needed or mgr_needed:
                orders_to_hold |= order
                vals = {'state': 'waiting_approval'}
                pending_gates = []
                if cust_needed:
                    vals['customer_approval_state'] = 'pending'
                    pending_gates.append(_("Customer Sign-Off"))
                if mgr_needed:
                    vals['manager_approval_state'] = 'pending'
                    pending_gates.append(_("Sales Manager Approval"))

                order.write(vals)
                restricted_products = order.order_line.filtered(
                    lambda l: (l.require_customer_approval or l.require_manager_approval) and not l.display_type
                ).mapped('product_id.display_name')

                order.message_post(
                    body=Markup(_(
                        "Order routed to <b>Waiting Approval</b> due to restricted product(s): <i>%s</i>.<br/>"
                        "Pending Approval Gates: <b>%s</b>"
                    )) % (", ".join(restricted_products), " & ".join(pending_gates))
                )

        ready_orders = self - orders_to_hold
        if ready_orders:
            return super(SaleOrder, ready_orders).action_confirm()
        return True

    def action_customer_approve(self):
        self.ensure_one()
        self.write({
            'customer_approval_state': 'approved',
            'customer_approval_date': fields.Datetime.now(),
            'customer_approval_user_id': self.env.user.id,
        })
        self.message_post(body=Markup(_("<b>Customer Sign-Off</b> completed and recorded by %s.")) % self.env.user.name)
        if not self.needs_manager_approval or self.manager_approval_state == 'approved':
            return self.action_confirm()

    def action_manager_approve(self):
        self.ensure_one()
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            raise UserError(_("Only users with Sales Manager privileges can grant Manager Approval."))
        self.write({
            'manager_approval_state': 'approved',
            'manager_approval_date': fields.Datetime.now(),
            'manager_approval_user_id': self.env.user.id,
        })
        self.message_post(body=Markup(_("<b>Sales Manager Approval</b> granted by %s.")) % self.env.user.name)
        if not self.needs_customer_approval or self.customer_approval_state == 'approved':
            return self.action_confirm()

    def action_approval_reject(self):
        self.ensure_one()
        self.write({
            'state': 'cancel',
            'customer_approval_state': 'rejected' if self.needs_customer_approval else 'not_required',
            'manager_approval_state': 'rejected' if self.needs_manager_approval else 'not_required',
        })
        self.message_post(body=_("Order approval was <b>Rejected</b> by %s. Order has been cancelled.") % self.env.user.name)
