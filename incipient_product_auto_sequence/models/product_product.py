from odoo import api, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('default_code'):
                tmpl = False
                categ_id = vals.get('categ_id')
                if vals.get('product_tmpl_id'):
                    tmpl = self.env['product.template'].browse(vals['product_tmpl_id'])
                    if not categ_id:
                        categ_id = tmpl.categ_id.id
                    # If template already has a default_code, use it for the variant
                    if tmpl.default_code:
                        vals['default_code'] = tmpl.default_code
                        continue
                if categ_id:
                    category = self.env['product.category'].browse(categ_id)
                    if category.auto_sequence and category.sequence_id:
                        vals['default_code'] = category.sequence_id.next_by_id()
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if 'categ_id' in vals and vals['categ_id']:
            new_categ = self.env['product.category'].browse(vals['categ_id'])
            if new_categ.auto_sequence and new_categ.sequence_id:
                for product in self:
                    if 'default_code' not in vals:
                        product.default_code = new_categ.sequence_id.next_by_id()
        return res

