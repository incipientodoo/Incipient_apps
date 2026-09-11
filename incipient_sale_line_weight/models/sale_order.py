from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    unit_weight = fields.Float(
        string="Unit Weight",
        digits=(16, 2),
        related='product_template_id.weight',
        store=True
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

    @api.depends('product_uom_qty', 'unit_weight')
    def _compute_ext_weight(self):
        for line in self:
            line.ext_weight = line.product_uom_qty * line.unit_weight

    @api.depends('order_id.order_line.ext_weight', 'order_id.order_line.display_type')
    def _compute_section_total_weight(self):
        for line in self:
            if line.display_type == 'line_section':
                total_weight = 0.0
                in_section = False
                for ol in line.order_id.order_line:
                    if ol == line:
                        in_section = True
                        continue
                    if in_section:
                        if ol.display_type == 'line_section':
                            break
                        total_weight += ol.ext_weight or 0.0
                line.section_total_weight = total_weight
            else:
                line.section_total_weight = 0.0

