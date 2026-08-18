from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ExtractionReportWizard(models.TransientModel):
    _name = 'extraction.report.wizard'
    _description = 'Generate Extraction Report'

    date_from = fields.Date(string='Period Start', required=True)
    date_to = fields.Date(string='Period End', required=True)
    vendor_ids = fields.Many2many(
        'res.partner',
        string='Manufacturers',
        domain=[('supplier_rank', '>', 0)],
        help='Leave empty for all manufacturers.',
    )

    def action_generate(self):
        self.ensure_one()
        ExtractionLine = self.env['extraction.report.line']

        existing = ExtractionLine.search([
            ('period_start', '=', self.date_from),
            ('period_end', '=', self.date_to),
        ])
        existing.unlink()

        domain = [
            ('order_id.state', 'in', ['sale', 'done']),
            ('order_id.date_order', '>=', self.date_from),
            ('order_id.date_order', '<=', self.date_to),
        ]
        sale_lines = self.env['sale.order.line'].search(domain)

        contract_products = self.env['vendor.contract.line'].search([
            ('state', '=', 'active'),
        ]).mapped('product_id')

        lines_data = []
        today = fields.Date.today()

        for sl in sale_lines:
            product = sl.product_id
            if not product or product not in contract_products:
                continue

            contract_line = self.env['vendor.contract.line'].search([
                ('product_id', '=', product.id),
                ('state', '=', 'active'),
                ('date_start', '<=', sl.order_id.date_order),
                ('date_end', '>=', sl.order_id.date_order),
            ], limit=1, order='contract_net_cost asc')

            if not contract_line:
                continue

            if self.vendor_ids and contract_line.vendor_id not in self.vendor_ids:
                continue

            fifo_cost = product.standard_price
            contract_net = contract_line.contract_net_cost
            rebate_per_unit = fifo_cost - contract_net
            qty = sl.product_uom_qty

            invoice = False
            if sl.invoice_lines:
                invoice = sl.invoice_lines[0].move_id.id

            lines_data.append({
                'extraction_date': today,
                'period_start': self.date_from,
                'period_end': self.date_to,
                'vendor_id': contract_line.vendor_id.id,
                'customer_id': sl.order_id.partner_id.id,
                'product_id': product.id,
                'contract_id': contract_line.contract_id.id,
                'qty_sold': qty,
                'fifo_cost': fifo_cost,
                'contract_net_cost': contract_net,
                'rebate_per_unit': rebate_per_unit,
                'total_rebate': rebate_per_unit * qty,
                'sale_order_id': sl.order_id.id,
                'sale_line_id': sl.id,
                'invoice_id': invoice,
            })

        if not lines_data:
            raise UserError(_('No contract-linked sales found for this period.'))

        ExtractionLine.create(lines_data)

        return {
            'type': 'ir.actions.act_window',
            'name': f'Extraction: {self.date_from} to {self.date_to}',
            'res_model': 'extraction.report.line',
            'view_mode': 'list,pivot,graph',
            'domain': [
                ('period_start', '=', self.date_from),
                ('period_end', '=', self.date_to),
            ],
            'context': {
                'search_default_group_vendor': 1,
                'search_default_group_customer': 1,
            },
        }