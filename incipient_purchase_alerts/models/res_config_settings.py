from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    enable_po_change_alert = fields.Boolean(
        string='Alert on PO Quantity/Price Change',
        default=True,
        help='Send email notifications when confirmed PO line quantity or price is modified.'
    )
    po_change_alert_user_ids = fields.Many2many(
        'res.users',
        'company_po_change_user_rel',
        'company_id', 'user_id',
        string='PO Change Alert Recipients'
    )

    enable_po_price_increase_alert = fields.Boolean(
        string='Alert on Product Price Increase',
        default=True,
        help='Alert buyers when a PO unit price is higher than the vendor/product last purchase price.'
    )
    po_price_increase_alert_user_ids = fields.Many2many(
        'res.users',
        'company_po_price_inc_user_rel',
        'company_id', 'user_id',
        string='Price Increase Alert Recipients'
    )

    enable_receipt_confirm_alert = fields.Boolean(
        string='Alert on Receipt Confirmation',
        default=True,
        help='Send email notifications when stock receipts for a Purchase Order are completed.'
    )
    receipt_confirm_alert_user_ids = fields.Many2many(
        'res.users',
        'company_receipt_confirm_user_rel',
        'company_id', 'user_id',
        string='Receipt Confirmation Alert Recipients'
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_po_change_alert = fields.Boolean(
        related='company_id.enable_po_change_alert',
        readonly=False,
        string='Alert on PO Quantity/Price Change'
    )
    po_change_alert_user_ids = fields.Many2many(
        related='company_id.po_change_alert_user_ids',
        readonly=False,
        string='PO Change Alert Recipients'
    )

    enable_po_price_increase_alert = fields.Boolean(
        related='company_id.enable_po_price_increase_alert',
        readonly=False,
        string='Alert on Product Price Increase'
    )
    po_price_increase_alert_user_ids = fields.Many2many(
        related='company_id.po_price_increase_alert_user_ids',
        readonly=False,
        string='Price Increase Alert Recipients'
    )

    enable_receipt_confirm_alert = fields.Boolean(
        related='company_id.enable_receipt_confirm_alert',
        readonly=False,
        string='Alert on Receipt Confirmation'
    )
    receipt_confirm_alert_user_ids = fields.Many2many(
        related='company_id.receipt_confirm_alert_user_ids',
        readonly=False,
        string='Receipt Confirmation Alert Recipients'
    )
