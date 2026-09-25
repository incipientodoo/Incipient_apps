from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    additional_discount = fields.Float(string="Additional Discount (%)",copy=False)
    sale_discount = fields.Float(string="Volume Discount(%)", copy=False)
    discount = fields.Float(copy=False)
    sale_discount_amount = fields.Float(compute="_compute_sale_discount_amount")
    additional_discount_amount = fields.Float(compute="_compute_additional_discount_amount")
    total_discount_amount = fields.Float(compute="_compute_total_discount_amount")
    is_additional_discount = fields.Boolean()

    def _compute_additional_discount_amount(self):
        for rec in self:
            rec.additional_discount_amount = (rec.price_unit * rec.product_uom_qty * rec.additional_discount)/100

    def _compute_sale_discount_amount(self):
        for rec in self:
            rec.sale_discount_amount = (rec.price_unit * rec.product_uom_qty * rec.sale_discount)/100

    def _compute_total_discount_amount(self):
        for rec in self:
            rec.total_discount_amount = (rec.price_unit * rec.product_uom_qty * rec.discount)/100

    @api.onchange('additional_discount','sale_discount')
    def _onchange_additional_discount(self):
        for line in self:
            rule_discount = line.sale_discount  # Existing discount
            additional_discount = line.additional_discount or 0.0
            line.discount = rule_discount + additional_discount
