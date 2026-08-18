from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    # vendor custom field
    network_account = fields.Boolean("Network Account")
    dedicated_network_account_number = fields.Char("Dedicated Network Account Number")
    acc_number = fields.Char("Account Number")
    max_date = fields.Date("Max Date")
    dollar_ytd = fields.Float("Dollars Y-T-D")
    discount = fields.Float("Discount %")
    days = fields.Integer("Days")
    net = fields.Integer("Net")
    discount_2 = fields.Float("Second Discount %")
    days_2 = fields.Integer("Days 2")
    net_2 = fields.Integer("Net 2")
    payment_term = fields.Many2one("account.payment.term", "Payment Term")
    default_ap_gl = fields.Char("Default AP GL Number")
    last_pay = fields.Date("Last Pay")
    default_gl = fields.Char("Default GL Number")
    zip_4 = fields.Char("Zip + 4")
    # customer custom field
    customer_number = fields.Char("Customer Number")
    cost_level = fields.Selection([
        ('cost_2', 'Cost 2'),
        ('cost_3', 'Cost 3'),
        ('custom', 'Custom'),
    ], string='Cost Level', tracking=True,
        help='Assigned cost level. Cost 2 and Cost 3 represent manufacturer cost plus a defined markup %.')
    cost_markup_percentage = fields.Float(
        string='Markup %',
        help='If cost level is Custom, specify the markup percentage over manufacturer cost.',
    )
    discretionary_price_ids = fields.One2many(
        'discretionary.price',
        'customer_id',
        string='Active Price Overrides',
    )
    discretionary_price_count = fields.Integer(
        compute='_compute_discretionary_price_count',
    )

    def _compute_discretionary_price_count(self):
        for partner in self:
            partner.discretionary_price_count = self.env['discretionary.price'].search_count([
                ('customer_id', '=', partner.id),
                ('is_expired', '=', False),
            ])

    def action_view_discretionary_prices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Price Overrides',
            'res_model': 'discretionary.price',
            'view_mode': 'list,form',
            'domain': [('customer_id', '=', self.id)],
            'context': {'default_customer_id': self.id},
        }


