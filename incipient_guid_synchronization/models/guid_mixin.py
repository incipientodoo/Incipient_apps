# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields, api

def _generate_guid(self):
    return str(uuid.uuid4())

class ResPartner(models.Model):
    _inherit = 'res.partner'

    guid = fields.Char(string="GUID", copy=False, index=True, tracking=True, default=_generate_guid)
    
    _sql_constraints = [
        ('unique_guid_partner', 'unique(guid)', 'The GUID must be unique!')
    ]

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    guid = fields.Char(string="GUID", copy=False, index=True, tracking=True, default=_generate_guid)

    _sql_constraints = [
        ('unique_guid_lead', 'unique(guid)', 'The GUID must be unique!')
    ]

class SaleOrder(models.Model):
    _inherit = "sale.order"

    guid = fields.Char(string="GUID", copy=False, index=True, tracking=True, default=_generate_guid)

    _sql_constraints = [
        ('unique_guid_so', 'unique(guid)', 'The GUID must be unique!')
    ]

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    guid = fields.Char(string="GUID", copy=False, index=True, tracking=True, default=_generate_guid)

    _sql_constraints = [
        ('unique_guid_sol', 'unique(guid)', 'The GUID must be unique!')
    ]

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    guid = fields.Char(string="GUID", copy=False, index=True, tracking=True, default=_generate_guid)

    _sql_constraints = [
        ('unique_guid_po', 'unique(guid)', 'The GUID must be unique!')
    ]

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    guid = fields.Char(string="GUID", copy=False, index=True, tracking=True, default=_generate_guid)

    _sql_constraints = [
        ('unique_guid_pol', 'unique(guid)', 'The GUID must be unique!')
    ]

class AccountMove(models.Model):
    _inherit = "account.move"

    guid = fields.Char(string="GUID", copy=False, index=True, tracking=True, default=_generate_guid)

    _sql_constraints = [
        ('unique_guid_am', 'unique(guid)', 'The GUID must be unique!')
    ]

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    guid = fields.Char(string="GUID", copy=False, index=True, tracking=True, default=_generate_guid)

    _sql_constraints = [
        ('unique_guid_aml', 'unique(guid)', 'The GUID must be unique!')
    ]
