# -*- coding: utf-8 -*-
from odoo import fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    require_customer_approval = fields.Boolean(
        string="Requires Customer Sign-Off",
        related='product_template_id.require_customer_approval',
        store=True
    )
    require_manager_approval = fields.Boolean(
        string="Requires Manager Approval",
        related='product_template_id.require_manager_approval',
        store=True
    )
