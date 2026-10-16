# -*- coding: utf-8 -*-
from odoo import api, models

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        if self.env.context.get('ignore_hidden_menu_ids'):
            return res
        user = self.env.user
        if user and user.hidden_menu_ids:
            all_hidden_ids = set()
            current = user.hidden_menu_ids
            while current:
                all_hidden_ids.update(current.ids)
                current = self.sudo().search([('parent_id', 'in', current.ids)])
            return list(set(res) | all_hidden_ids)
        return res

    def _filter_visible_menus(self):
        visible_menus = super()._filter_visible_menus()
        if self.env.context.get('ignore_hidden_menu_ids'):
            return visible_menus
        user = self.env.user
        if user and user.hidden_menu_ids:
            blacklisted_ids = set(self._load_menus_blacklist())
            if blacklisted_ids:
                return visible_menus.filtered(lambda m: m.id not in blacklisted_ids)
        return visible_menus
