from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            categ_id = vals.get('categ_id')
            if categ_id and not vals.get('default_code'):
                category = self.env['product.category'].browse(categ_id)
                if category.auto_sequence and category.sequence_id:
                    vals['default_code'] = category.sequence_id.next_by_id()
        templates = super().create(vals_list)
        return templates

    def write(self, vals):
        if 'categ_id' in vals and vals['categ_id']:
            new_categ = self.env['product.category'].browse(vals['categ_id'])
            if new_categ.auto_sequence and new_categ.sequence_id:
                for tmpl in self:
                    # If default_code is not explicitly set in write vals, generate new sequence from category
                    if 'default_code' not in vals:
                        code = new_categ.sequence_id.next_by_id()
                        tmpl.default_code = code
                        # Synchronize variants default_code
                        if len(tmpl.product_variant_ids) == 1:
                            tmpl.product_variant_ids.default_code = code
        return super().write(vals)
