from odoo import models, fields


class CustomerDivision(models.Model):
    _name = 'customer.division'

    div_code = fields.Char("Division Code")
    div_name = fields.Char("Division Name")