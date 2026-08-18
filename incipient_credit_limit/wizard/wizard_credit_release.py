from odoo import models, fields, _

class WizardCreditRelease(models.TransientModel):
    _name = 'wizard.credit.release'
    _description = 'Credit Release Wizard'

    order_id = fields.Many2one('sale.order', string='Order', required=True)
    reason = fields.Text(string='Reason', required=True)

    def action_release(self):
        self.ensure_one()
        self.order_id.with_context(skip_credit_check=True).write({'is_credit_hold': False})
        self.order_id.message_post(
            body=_("✅ Credit Hold released by %s.\nReason: %s") % (self.env.user.name, self.reason)
        )
        return {'type': 'ir.actions.act_window_close'}
