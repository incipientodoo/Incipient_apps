# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    require_customer_approval = fields.Boolean(
        string="Requires Customer Sign-Off",
        help="If enabled, sales orders containing this product require customer approval/sign-off before confirmation.",
        tracking=True
    )
    require_manager_approval = fields.Boolean(
        string="Requires Sales Manager Approval",
        help="If enabled, sales orders containing this product require sales manager approval before confirmation.",
        tracking=True
    )
