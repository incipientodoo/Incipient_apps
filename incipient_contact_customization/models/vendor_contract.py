from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VendorContract(models.Model):
    _name = 'vendor.contract'
    _description = 'Vendor Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(
        string='Contract Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    vendor_id = fields.Many2one(
        'res.partner',
        string='Manufacturer / Vendor',
        required=True,
        domain=[('supplier_rank', '>', 0)],
        tracking=True,
    )
    source = fields.Selection([
        ('manufacturer', 'Direct from Manufacturer'),
        ('network', 'Network'),
    ], string='Contract Source', required=True, tracking=True)
    date_start = fields.Date(string='Start Date', required=True, tracking=True)
    date_end = fields.Date(string='End Date', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    line_ids = fields.One2many(
        'vendor.contract.line',
        'contract_id',
        string='Contract Lines',
    )
    notes = fields.Html(string='Notes')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    line_count = fields.Integer(
        string='Item Count',
        compute='_compute_line_count',
    )

    @api.depends('line_ids')
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('vendor.contract') or _('New')
        return super().create(vals_list)

    def action_activate(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_('Cannot activate a contract with no lines.'))
            rec.state = 'active'

    def action_expire(self):
        self.write({'state': 'expired'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def _cron_check_expiration(self):
        today = fields.Date.today()
        expired = self.search([
            ('state', '=', 'active'),
            ('date_end', '<', today),
        ])
        expired.write({'state': 'expired'})

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError(_('End Date must be after Start Date.'))


class VendorContractLine(models.Model):
    _name = 'vendor.contract.line'
    _description = 'Vendor Contract Line'
    _order = 'contract_id, product_id'

    contract_id = fields.Many2one(
        'vendor.contract',
        string='Contract',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        related='product_id.product_tmpl_id',
        string='Product Template',
        store=True,
    )
    contract_net_cost = fields.Float(
        string='Contract Net Cost',
        digits='Product Price',
        required=True,
    )
    fifo_cost = fields.Float(
        string='FIFO In-Stock Cost',
        digits='Product Price',
        compute='_compute_fifo_cost',
        store=True,
    )
    rebate_amount = fields.Float(
        string='Rebate Amount',
        digits='Product Price',
        compute='_compute_rebate_amount',
        store=True,
    )
    vendor_id = fields.Many2one(
        related='contract_id.vendor_id',
        string='Manufacturer',
        store=True,
    )
    date_start = fields.Date(related='contract_id.date_start', store=True)
    date_end = fields.Date(related='contract_id.date_end', store=True)
    state = fields.Selection(related='contract_id.state', store=True)

    @api.depends('product_id')
    def _compute_fifo_cost(self):
        for line in self:
            if line.product_id:
                line.fifo_cost = line.product_id.standard_price
            else:
                line.fifo_cost = 0.0

    @api.depends('fifo_cost', 'contract_net_cost')
    def _compute_rebate_amount(self):
        for line in self:
            line.rebate_amount = line.fifo_cost - line.contract_net_cost


class CustomerContract(models.Model):
    _name = 'customer.contract'
    _description = 'Customer Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc, id desc'

    name = fields.Char(
        string='Contract Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        domain=[('customer_rank', '>', 0)],
        tracking=True,
    )
    source = fields.Selection([
        ('direct', 'Direct'),
        ('network', 'Network'),
    ], string='Contract Source', required=True, tracking=True)
    date_start = fields.Date(string='Start Date', required=True, tracking=True)
    date_end = fields.Date(string='End Date', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    line_ids = fields.One2many(
        'customer.contract.line',
        'contract_id',
        string='Contract Lines',
    )
    notes = fields.Html(string='Notes')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )
    line_count = fields.Integer(
        string='Item Count',
        compute='_compute_line_count',
    )

    @api.depends('line_ids')
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('customer.contract') or _('New')
        return super().create(vals_list)

    def action_activate(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_('Cannot activate a contract with no lines.'))
            rec.state = 'active'

    def action_expire(self):
        self.write({'state': 'expired'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def _cron_check_expiration(self):
        today = fields.Date.today()
        expired = self.search([
            ('state', '=', 'active'),
            ('date_end', '<', today),
        ])
        expired.write({'state': 'expired'})

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError(_('End Date must be after Start Date.'))


class CustomerContractLine(models.Model):
    _name = 'customer.contract.line'
    _description = 'Customer Contract Line'
    _order = 'contract_id, product_id'

    contract_id = fields.Many2one(
        'customer.contract',
        string='Contract',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        related='product_id.product_tmpl_id',
        string='Product Template',
        store=True,
    )
    cost_price = fields.Float(
        string='Cost Price',
        digits='Product Price',
        required=True,
    )
    partner_id = fields.Many2one(
        related='contract_id.partner_id',
        string='Customer',
        store=True,
    )
    date_start = fields.Date(related='contract_id.date_start', store=True)
    date_end = fields.Date(related='contract_id.date_end', store=True)
    state = fields.Selection(related='contract_id.state', store=True)
