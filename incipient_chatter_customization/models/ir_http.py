from odoo import models

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super().session_info()
        user_id = self.env.user.id
        # Get all chatter configs for the current user
        configs = self.env['chatter.config'].sudo().search([
            ('user_ids', 'in', user_id)
        ])
        
        hidden_models = configs.filtered(lambda c: c.hide_send_message).mapped('model_id.model')
        collapsible_models = configs.filtered(lambda c: c.enable_collapse).mapped('model_id.model')
        
        res['chatter_hidden_models'] = hidden_models
        res['chatter_collapsible_models'] = collapsible_models
        return res
