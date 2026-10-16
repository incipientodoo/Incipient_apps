# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command

class ResUsers(models.Model):
    _inherit = 'res.users'

    hidden_menu_ids = fields.Many2many(
        'ir.ui.menu',
        'res_users_hidden_menu_rel',
        'user_id',
        'menu_id',
        string='Hidden Menus',
        domain="[('id', 'in', accessible_menu_ids)]",
        help='Specific menu items hidden from this user. All child sub-menus will also be hidden.'
    )

    accessible_menu_ids = fields.Many2many(
        'ir.ui.menu',
        compute='_compute_accessible_menu_ids',
        store=False,
    )

    @api.depends('group_ids')
    def _compute_accessible_menu_ids(self):
        for user in self:
            if not user.id:
                user.accessible_menu_ids = self.env['ir.ui.menu']
                continue
            
            menu_dict = self.env['ir.ui.menu'].with_user(user).with_context(ignore_hidden_menu_ids=True).load_menus(False)
            
            visible_ids = [m_id for m_id in menu_dict.keys() if isinstance(m_id, int)]
            user.accessible_menu_ids = self.env['ir.ui.menu'].browse(visible_ids)

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        group_user = self.env.ref('base.group_user', raise_if_not_found=False)
        if group_user:
            for user in users:
                if group_user not in user.group_ids and user.hidden_menu_ids:
                    user.hidden_menu_ids = [Command.clear()]
        return users

    def write(self, vals):
        res = super().write(vals)
        group_user = self.env.ref('base.group_user', raise_if_not_found=False)
        if group_user:
            for user in self:
                if group_user not in user.group_ids and user.hidden_menu_ids:
                    user.hidden_menu_ids = [Command.clear()]
        if 'hidden_menu_ids' in vals or 'group_ids' in vals:
            self.env.registry.clear_cache()
        return res
