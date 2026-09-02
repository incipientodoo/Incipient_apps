# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleDelayReasonWizard(models.TransientModel):
    _name = "sale.delay.reason.wizard"
    _description = "Reason for Delay Wizard"

    sale_order_id = fields.Many2one("sale.order", string="Sale Order", required=True, readonly=True)
    reason_for_delay = fields.Char("Reason for Delay", required=True)

    def action_confirm_with_reason(self):
        self.ensure_one()
        order = self.sale_order_id
        order.reason_for_delay = self.reason_for_delay
        return order.action_confirm()
