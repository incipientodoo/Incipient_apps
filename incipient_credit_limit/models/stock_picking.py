from odoo import models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            if picking.picking_type_id.code == 'outgoing' and picking.sale_id:
                partner = picking.sale_id.partner_id
                
                # Check Past Due
                total_overdue = partner.total_overdue if hasattr(partner, 'total_overdue') else 0.0
                if total_overdue > 0:
                    raise UserError(_(
                        "Shipping Blocked: This customer has a past due balance of %.2f.\n"
                        "Please have the accounting team review and clear their account before shipping."
                    ) % total_overdue)
                
                # Check Credit Limit (Total outstanding AR)
                credit_limit = partner.credit_limit
                if credit_limit > 0:
                    # In Odoo, partner.credit holds the total Accounts Receivable (unpaid invoices)
                    total_owed = partner.credit if hasattr(partner, 'credit') else 0.0
                    if total_owed > credit_limit:
                        raise UserError(_(
                            "Shipping Blocked: This customer has exceeded their credit limit.\n"
                            "Credit Limit: %.2f\n"
                            "Current Outstanding Balance: %.2f\n"
                            "Please have the accounting team review before shipping."
                        ) % (credit_limit, total_owed))
                        
        return super().button_validate()
