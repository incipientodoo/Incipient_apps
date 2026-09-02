# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    reason_for_delay = fields.Char(string="Reason for Delay", tracking=True)

    def action_confirm(self):
        for order in self:
            if order.commitment_date and order.commitment_date.date() < date.today() and not order.reason_for_delay:
                return {
                    'name': _('Reason for Delay'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.delay.reason.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_sale_order_id': order.id,
                    },
                }
        return super(SaleOrder, self).action_confirm()
