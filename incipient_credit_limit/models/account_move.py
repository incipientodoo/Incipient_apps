from odoo import models

class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        res = super().write(vals)
        print("\n\n\n",vals)
        # if 'payment_state' in vals:
            # print("\n\n\npayment_state",vals['payment_state'])
        for move in self:
            print("\n\n\nmove",move)
            print("\n\n\nmove.payment_state",move.payment_state)
            if move.payment_state in ('paid', 'in_payment'):
                print("\n\n\nmove.partner_id",move.partner_id)
                if move.partner_id:
                    print("\n\n\npartner")
                    move.partner_id._auto_release_credit_holds()
        return res

