import base64
import io

from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    import openpyxl
except ImportError:
    openpyxl = None


class ContractImportWizard(models.TransientModel):
    _name = 'contract.import.wizard'
    _description = 'Import Contract from Excel'

    vendor_id = fields.Many2one(
        'res.partner',
        string='Manufacturer / Vendor',
        required=True,
        domain=[('supplier_rank', '>', 0)],
    )
    source = fields.Selection([
        ('manufacturer', 'Direct from Manufacturer'),
        ('network', 'Network'),
    ], string='Contract Source', required=True, default='manufacturer')
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    file_data = fields.Binary(string='Excel File', required=True)
    file_name = fields.Char(string='File Name')
    product_column = fields.Char(
        string='Product Column',
        default='A',
        help='Column letter containing product Internal Reference.',
    )
    cost_column = fields.Char(
        string='Contract Net Cost Column',
        default='B',
        help='Column letter containing the contract net cost.',
    )
    header_row = fields.Integer(
        string='Header Row',
        default=1,
        help='Row number of headers (data starts from next row).',
    )

    def action_import(self):
        self.ensure_one()
        if not openpyxl:
            raise UserError(_('openpyxl library is required.'))

        file_content = base64.b64decode(self.file_data)
        wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True)
        ws = wb.active

        contract = self.env['vendor.contract'].create({
            'vendor_id': self.vendor_id.id,
            'source': self.source,
            'date_start': self.date_start,
            'date_end': self.date_end,
        })

        Product = self.env['product.product']
        lines_data = []
        errors = []
        row_num = 0

        for row in ws.iter_rows(min_row=self.header_row + 1, values_only=False):
            row_num += 1
            prod_col_idx = ord(self.product_column.upper()) - ord('A')
            cost_col_idx = ord(self.cost_column.upper()) - ord('A')

            if prod_col_idx >= len(row) or cost_col_idx >= len(row):
                continue

            product_ref = row[prod_col_idx].value
            cost_val = row[cost_col_idx].value

            if not product_ref or not cost_val:
                continue

            product_ref = str(product_ref).strip()
            product = Product.search([
                '|',
                ('default_code', '=', product_ref),
                ('barcode', '=', product_ref),
            ], limit=1)

            if not product:
                errors.append(f"Row {self.header_row + row_num}: Product '{product_ref}' not found.")
                continue

            try:
                cost_val = float(cost_val)
            except (ValueError, TypeError):
                errors.append(f"Row {self.header_row + row_num}: Invalid cost '{cost_val}'.")
                continue

            lines_data.append({
                'contract_id': contract.id,
                'product_id': product.id,
                'contract_net_cost': cost_val,
            })

        if lines_data:
            self.env['vendor.contract.line'].create(lines_data)

        wb.close()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.contract',
            'res_id': contract.id,
            'view_mode': 'form',
            'target': 'current',
        }