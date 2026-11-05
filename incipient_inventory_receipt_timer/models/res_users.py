from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    active_receipt_timer_id = fields.Many2one(
        'stock.picking', 
        string="Active Receipt Timer", 
        copy=False,
        help="Tracks the receipt on which the user currently has an active timer running."
    )
