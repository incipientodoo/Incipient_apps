from odoo import api, fields, models, _

class ProductCategory(models.Model):
    _inherit = 'product.category'

    auto_sequence = fields.Boolean(
        string='Auto-Sequence Internal Ref',
        default=False,
        help='If enabled, products created or re-categorized in this category receive auto-generated internal references.'
    )
    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Internal Reference Sequence',
        domain="[('code', '=', 'product.category.auto.sequence')]",
        ondelete='restrict',
        copy=False,
        help='Sequence used to generate internal references for products in this category.'
    )
    sequence_prefix = fields.Char(
        string='Sequence Prefix',
        help='Custom prefix for auto-created sequence, e.g., ELEC-'
    )

    @api.model_create_multi
    def create(self, vals_list):
        categories = super().create(vals_list)
        for category in categories:
            if category.auto_sequence and not category.sequence_id:
                category._create_category_sequence()
        return categories

    def write(self, vals):
        res = super().write(vals)
        for category in self:
            if category.auto_sequence and not category.sequence_id:
                category._create_category_sequence()
            elif category.sequence_id and 'sequence_prefix' in vals:
                category.sequence_id.prefix = category.sequence_prefix or (category.name[:3].upper() + '-') if category.name else 'PRD-'
            elif category.sequence_id and 'name' in vals and not category.sequence_prefix:
                category.sequence_id.prefix = (category.name[:3].upper() + '-') if category.name else 'PRD-'
        return res


    def _create_category_sequence(self):
        self.ensure_one()
        prefix = self.sequence_prefix or (self.name[:3].upper() + '-') if self.name else 'PRD-'
        seq_vals = {
            'name': f'Internal Reference Sequence - {self.name}',
            'code': 'product.category.auto.sequence',
            'prefix': prefix,
            'padding': 5,
            'number_next': 1,
            'number_increment': 1,
            'company_id': False,
        }
        seq = self.env['ir.sequence'].create(seq_vals)
        self.sequence_id = seq.id

    def action_create_sequence(self):
        for category in self:
            if not category.sequence_id:
                category._create_category_sequence()
            category.auto_sequence = True
