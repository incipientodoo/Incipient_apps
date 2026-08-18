from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DiscretionaryPrice(models.Model):
    _name = 'discretionary.price'
    _description = 'Discretionary / Contract Price Override'
    _inherit = ['mail.thread']
    _order = 'expiration_date asc, customer_id, product_id'

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        domain=[('customer_rank', '>', 0)],
        tracking=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        tracking=True,
    )
    source_type = fields.Selection([
        ('contract', 'Contract'),
        ('discretionary', 'Discretionary (Owner)'),
    ], string='Price Source', required=True, default='discretionary', tracking=True)
    contract_id = fields.Many2one(
        'vendor.contract',
        string='Linked Contract',
    )
    override_cost = fields.Float(
        string='Override Cost',
        digits='Product Price',
        required=True,
        tracking=True,
    )
    resale_price = fields.Float(
        string='Resale Price',
        digits='Product Price',
        tracking=True,
    )
    expiration_date = fields.Date(
        string='Expiration Date',
        required=True,
        tracking=True,
    )
    is_expired = fields.Boolean(
        string='Expired',
        compute='_compute_is_expired',
        store=True,
    )
    vendor_id = fields.Many2one(
        'res.partner',
        string='Manufacturer',
        domain=[('supplier_rank', '>', 0)],
    )
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    @api.depends('expiration_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_expired = rec.expiration_date and rec.expiration_date < today

    @api.constrains('expiration_date')
    def _check_expiration_date(self):
        for rec in self:
            if not rec.expiration_date:
                raise ValidationError(_('Expiration Date is required.'))