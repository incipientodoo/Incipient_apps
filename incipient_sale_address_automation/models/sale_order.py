from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('partner_id', 'opportunity_id')
    def _compute_partner_shipping_id(self):
        for order in self:
            partner = order.partner_id
            if order.opportunity_id and order.opportunity_id.active and order.opportunity_id.partner_id:
                partner = order.opportunity_id.partner_id
                
            if partner:
                order.partner_shipping_id = partner.address_get(['delivery'])['delivery']
            else:
                order.partner_shipping_id = False

    @api.depends('partner_id', 'opportunity_id')
    def _compute_partner_invoice_id(self):
        for order in self:
            partner = order.partner_id
            if order.opportunity_id and order.opportunity_id.active and order.opportunity_id.partner_id:
                partner = order.opportunity_id.partner_id
            
            if partner:
                commercial_partner = partner.commercial_partner_id or partner
                invoice_child = self.env['res.partner'].search([
                    ('parent_id', '=', commercial_partner.id),
                    ('type', '=', 'invoice')
                ], limit=1)
                
                if invoice_child:
                    order.partner_invoice_id = invoice_child.id
                elif hasattr(partner, 'primary_account_partner_id') and partner.primary_account_partner_id:
                    order.partner_invoice_id = partner.primary_account_partner_id.id
                else:
                    order.partner_invoice_id = partner.address_get(['invoice'])['invoice']
            else:
                order.partner_invoice_id = False
