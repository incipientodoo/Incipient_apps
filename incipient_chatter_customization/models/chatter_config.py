from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ChatterConfig(models.Model):
    _name = 'chatter.config'
    _description = 'Chatter Configuration'

    name = fields.Char(string='Name', required=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade', domain="[('is_mail_thread', '=', True)]")
    user_ids = fields.Many2many('res.users', string='Users')
    hide_send_message = fields.Boolean(string='Hide Send Message', default=True, help="If checked, the 'Send Message' button will be hidden for the selected users on the selected model.")
    enable_collapse = fields.Boolean(string='Enable Collapse', default=True, help="If checked, users can collapse/expand the Chatter panel.")

    @api.constrains('model_id', 'user_ids')
    def _check_duplicate_user_model(self):
        for config in self:
            if not config.model_id or not config.user_ids:
                continue
            # Search for other configs that have the same model and share at least one user
            domain = [
                ('id', '!=', config.id),
                ('model_id', '=', config.model_id.id),
                ('user_ids', 'in', config.user_ids.ids)
            ]
            duplicate = self.search(domain, limit=1)
            if duplicate:
                overlapping_users = config.user_ids & duplicate.user_ids
                user_names = ', '.join(overlapping_users.mapped('name'))
                raise ValidationError(f"Duplicate configuration found for model '{config.model_id.name}' and user(s): {user_names}")

