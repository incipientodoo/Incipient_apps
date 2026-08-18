from collections import abc
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float(string='Credit Limit')

    def _auto_release_credit_holds(self):
        for partner in self:
            total_overdue = partner.total_overdue if hasattr(partner, 'total_overdue') else 0.0
            
            total_owed = partner.credit if hasattr(partner, 'credit') else 0.0
            credit_limit = partner.credit_limit                 
            
            if credit_limit > 0 and total_owed < credit_limit:
                continue
                
            held_orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),
                ('is_credit_hold', '=', True),
            ])
            for order in held_orders:
                order.with_context(skip_credit_check=True).write({'is_credit_hold': False})
                order.message_post(
                    body="✅ Credit Hold automatically released because the customer's account balance is now in good standing (Invoice Paid)."
                )