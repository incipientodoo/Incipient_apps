from odoo import models, fields


class ExtractionLine(models.Model):
    _name = 'extraction.report.line'
    _description = 'Extraction Report Line'
    _order = 'vendor_id, customer_id, product_id'

    extraction_date = fields.Date(string='Extraction Date')
    period_start = fields.Date(string='Period Start')
    period_end = fields.Date(string='Period End')
    vendor_id = fields.Many2one('res.partner', string='Manufacturer')
    customer_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')
    contract_id = fields.Many2one('vendor.contract', string='Contract')
    qty_sold = fields.Float(string='Qty Sold', digits='Product Unit of Measure')
    fifo_cost = fields.Float(string='FIFO Cost (per unit)', digits='Product Price')
    contract_net_cost = fields.Float(string='Contract Net Cost', digits='Product Price')
    rebate_per_unit = fields.Float(string='Rebate Per Unit', digits='Product Price')
    total_rebate = fields.Float(string='Total Rebate Amount', digits='Product Price')
    sale_order_id = fields.Many2one('sale.order', string='Sales Order')
    sale_line_id = fields.Many2one('sale.order.line', string='SO Line')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )