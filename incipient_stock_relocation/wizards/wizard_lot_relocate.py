# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class WizardLotRelocate(models.TransientModel):
    _name = 'wizard.lot.relocate'
    _description = 'Lot Relocation Wizard'

    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number', required=True)
    product_id = fields.Many2one('product.product', related='lot_id.product_id', string='Product')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    source_location_id = fields.Many2one('stock.location', string='Source Location', required=True)
    dest_location_id = fields.Many2one('stock.location', string='Destination Location', required=True, domain="[('usage', '=', 'internal')]")
    
    available_qty = fields.Float(string='Available Quantity', readonly=True)
    relocate_qty = fields.Float(string='Quantity to Relocate', required=True, default=1.0)

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.lot_id:
            # Find the quant for this lot
            quants = self.env['stock.quant'].sudo().search([
                ('lot_id', '=', self.lot_id.id),
                ('location_id.usage', '=', 'internal')
            ])
            if quants:
                # Take the first location with positive quantity
                quant = quants.filtered(lambda q: q.quantity > 0)
                if quant:
                    quant = quant[0]
                    self.source_location_id = quant.location_id.id
                    self.available_qty = quant.quantity
                else:
                    self.source_location_id = False
                    self.available_qty = 0.0

    def action_relocate(self):
        self.ensure_one()
        if self.relocate_qty <= 0:
            raise ValidationError(_('Quantity to relocate must be positive.'))
        if self.relocate_qty > self.available_qty:
            raise ValidationError(_('Cannot relocate more than available quantity (%s).') % self.available_qty)
        if self.source_location_id == self.dest_location_id:
            raise ValidationError(_('Source and Destination locations cannot be the same.'))

        # Find internal operation type
        picking_type = self.env['stock.picking.type'].sudo().search([
            ('code', '=', 'internal'),
            ('warehouse_id.company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not picking_type:
            raise ValidationError(_('No internal transfer picking type found for this company.'))

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': self.source_location_id.id,
            'location_dest_id': self.dest_location_id.id,
            'move_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_qty': self.relocate_qty,
                'product_uom': self.product_id.uom_id.id,
                'location_id': self.source_location_id.id,
                'location_dest_id': self.dest_location_id.id,
            })],
        })
        
        picking.action_confirm()
        
        # Assign lot
        for move_line in picking.move_line_ids:
            move_line.lot_id = self.lot_id.id
            move_line.quantity = self.relocate_qty
            
        picking.button_validate()

        return {
            'name': _('Relocation Transfer'),
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'res_id': picking.id,
            'type': 'ir.actions.act_window',
        }
