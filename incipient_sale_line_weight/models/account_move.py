from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    unit_weight = fields.Float(
        string="Unit Weight",
        digits=(16, 2),
        related='product_id.product_tmpl_id.weight',
        store=True,
        help="Fetches the unit weight from the product template to match Sales Order."
    )

    section_total_weight = fields.Float(
        string="Section Total Weight",
        compute='_compute_section_total_weight',
        digits=(16, 2)
    )

    ext_weight = fields.Float(
        string="Ext Weight",
        compute='_compute_ext_weight',
        digits=(16, 2),
        store=True,
        help="Calculates extended weight as quantity × unit weight."
    )

    @api.depends('quantity', 'unit_weight')
    def _compute_ext_weight(self):
        for line in self:
            line.ext_weight = line.quantity * line.unit_weight

    @api.depends('move_id.invoice_line_ids.ext_weight', 'move_id.invoice_line_ids.display_type')
    def _compute_section_total_weight(self):
        for line in self:
            if line.display_type == 'line_section':
                total_weight = 0.0
                in_section = False
                for ml in line.move_id.invoice_line_ids:
                    if ml == line:
                        in_section = True
                        continue
                    if in_section:
                        if ml.display_type == 'line_section':
                            break
                        total_weight += ml.ext_weight or 0.0
                line.section_total_weight = total_weight
            else:
                line.section_total_weight = 0.0
