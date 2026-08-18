from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_contract_pricing = fields.Boolean(
        string='Has Contract Pricing',
        compute='_compute_has_contract_pricing',
    )
    customer_contract_id = fields.Many2one(
        'customer.contract',
        string='Customer Contract',
        tracking=True,
        domain="[('partner_id', '=', partner_id), ('state', '=', 'active')]",
        help='Active customer contract linked to this sale order.',
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_set_contract(self):
        """
        When the customer changes on the SO, auto-set the first active
        contract found for that customer. Clear if none exists.
        """
        self.customer_contract_id = False
        if self.partner_id:
            contract = self.env['customer.contract'].search([
                ('partner_id', '=', self.partner_id.id),
                ('state', '=', 'active'),
                ('date_start', '<=', fields.Date.today()),
                ('date_end', '>=', fields.Date.today()),
            ], limit=1, order='date_start desc')
            if contract:
                self.customer_contract_id = contract.id

    @api.depends('order_line.contract_line_id', 'order_line.discretionary_price_id')
    def _compute_has_contract_pricing(self):
        for order in self:
            order.has_contract_pricing = any(
                line.contract_line_id or line.discretionary_price_id
                for line in order.order_line
            )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    contract_line_id = fields.Many2one(
        'vendor.contract.line',
        string='Contract Line',
    )
    discretionary_price_id = fields.Many2one(
        'discretionary.price',
        string='Discretionary Price',
    )
    price_source = fields.Selection([
        ('pricelist', 'Pricelist'),
        ('contract', 'Vendor Contract'),
        ('discretionary', 'Discretionary Override'),
    ], string='Price Source', default='pricelist', readonly=True)
    original_cost = fields.Float(
        string='Original FIFO Cost',
        digits='Product Price',
    )
    override_cost = fields.Float(
        string='Applied Cost',
        digits='Product Price',
    )
    cost_expiration_date = fields.Date(
        string='Cost Expiration Date',
    )
    cost_price = fields.Float(
        string='Cost Price',
        digits='Product Price',
        help='Synced from/to customer contract',
    )

    @api.depends('product_id', 'product_uom_id', 'product_uom_qty')
    def _compute_price_unit(self):
        super()._compute_price_unit()
        for line in self:
            if not line.product_id or not line.order_partner_id:
                continue

            partner = line.order_partner_id
            product = line.product_id
            today = fields.Date.today()

            disc_price = self.env['discretionary.price'].search([
                ('customer_id', '=', partner.id),
                ('product_id', '=', product.id),
                ('expiration_date', '>=', today),
                ('is_expired', '=', False),
            ], limit=1, order='expiration_date asc')

            if disc_price:
                line.discretionary_price_id = disc_price.id
                line.contract_line_id = False
                line.price_source = 'discretionary'
                line.override_cost = disc_price.override_cost
                line.cost_expiration_date = disc_price.expiration_date
                line.original_cost = product.standard_price
                if disc_price.resale_price:
                    line.price_unit = disc_price.resale_price
                continue

            contract_line = self.env['vendor.contract.line'].search([
                ('product_id', '=', product.id),
                ('state', '=', 'active'),
                ('date_start', '<=', today),
                ('date_end', '>=', today),
            ], limit=1, order='contract_net_cost asc')

            if contract_line:
                line.contract_line_id = contract_line.id
                line.discretionary_price_id = False
                line.price_source = 'contract'
                line.override_cost = contract_line.contract_net_cost
                line.cost_expiration_date = contract_line.date_end
                line.original_cost = product.standard_price
                base_cost = contract_line.contract_net_cost
                markup_map = {
                    'cost_2': 0.02,
                    'cost_3': 0.05,
                }
                if partner.cost_level in markup_map:
                    line.price_unit = base_cost * (1 + markup_map[partner.cost_level])
                elif partner.cost_level == 'custom' and partner.cost_markup_percentage:
                    line.price_unit = base_cost * (1 + partner.cost_markup_percentage / 100)
                else:
                    line.price_unit = base_cost
                continue

            line.price_source = 'pricelist'
            line.contract_line_id = False
            line.discretionary_price_id = False
            line.override_cost = 0.0
            line.cost_expiration_date = False
            line.original_cost = product.standard_price

    @api.onchange('product_id')
    def _onchange_product_id_set_cost_price(self):
        """
        When a product is added/changed on the SO line:
        - Look up the linked customer contract for a matching product.
        - If found, set cost_price from the contract line.
        - If not found, leave cost_price as 0.
        """
        if not self.product_id or not self.order_id.customer_contract_id:
            self.cost_price = 0.0
            return

        contract = self.order_id.customer_contract_id
        contract_line = self.env['customer.contract.line'].search([
            ('contract_id', '=', contract.id),
            ('product_id', '=', self.product_id.id),
        ], limit=1)

        if contract_line:
            self.cost_price = contract_line.cost_price
        else:
            self.cost_price = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            line._sync_cost_price_to_contract()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if 'cost_price' in vals or 'product_id' in vals:
            for line in self:
                line._sync_cost_price_to_contract()
        return res

    def _sync_cost_price_to_contract(self):
        """
        Sync the cost_price from the SO line back into the customer contract:
        - If the product already exists in the contract → update cost_price.
        - If the product does NOT exist in the contract → create a new
          contract line with this product and cost_price.
        Only runs when both a contract and a product are set, and cost_price
        is non-zero.
        """
        self.ensure_one()
        contract = self.order_id.customer_contract_id
        if not contract or not self.product_id or not self.cost_price:
            return

        contract_line = self.env['customer.contract.line'].search([
            ('contract_id', '=', contract.id),
            ('product_id', '=', self.product_id.id),
        ], limit=1)

        if contract_line:
            if contract_line.cost_price != self.cost_price:
                contract_line.write({'cost_price': self.cost_price})
        else:
            # Create new line in the contract
            self.env['customer.contract.line'].create({
                'contract_id': contract.id,
                'product_id': self.product_id.id,
                'cost_price': self.cost_price,
            })
