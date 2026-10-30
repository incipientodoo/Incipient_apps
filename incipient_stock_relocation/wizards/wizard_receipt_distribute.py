# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class WizardReceiptDistribute(models.TransientModel):
    _name = 'wizard.receipt.distribute'
    _description = 'Receipt Distribution Wizard'

    picking_id = fields.Many2one('stock.picking', string='Receipt', required=True)
    line_ids = fields.One2many('wizard.receipt.distribute.line', 'wizard_id', string='Distribution Lines')

    @api.model
    def default_get(self, fields_list):
        res = super(WizardReceiptDistribute, self).default_get(fields_list)
        active_id = self._context.get('active_id')
        if active_id and self._context.get('active_model') == 'stock.picking':
            picking = self.env['stock.picking'].browse(active_id)
            lines = []
            for move in picking.move_ids.filtered(lambda m: m.state == 'done'):
                lines.append((0, 0, {
                    'move_id': move.id,
                    'qty_to_distribute': move.product_uom_qty,
                }))
            res['picking_id'] = active_id
            res['line_ids'] = lines
        return res

    def action_distribute(self):
        self.ensure_one()
        
        if not self.line_ids:
            raise ValidationError(_('Please add lines to distribute.'))
            
        # Validate quantities
        move_qty_map = {}
        for line in self.line_ids:
            if line.qty_to_distribute <= 0:
                raise ValidationError(_('Quantity to distribute must be positive.'))
            if line.move_id not in move_qty_map:
                move_qty_map[line.move_id] = 0.0
            move_qty_map[line.move_id] += line.qty_to_distribute
            
        for move, qty in move_qty_map.items():
            if qty > move.product_uom_qty:
                raise ValidationError(_('Cannot distribute more than the received quantity for product %s.') % move.product_id.display_name)

        # Group by destination location
        location_group = {}
        for line in self.line_ids:
            loc = line.dest_location_id
            if not loc:
                raise ValidationError(_('Destination location is required for all lines.'))
            if loc not in location_group:
                location_group[loc] = []
            location_group[loc].append(line)
            
        # Create pickings
        picking_type = self.env['stock.picking.type'].sudo().search([
            ('code', '=', 'internal'),
            ('warehouse_id.company_id', '=', self.picking_id.company_id.id)
        ], limit=1)
        
        if not picking_type:
            raise ValidationError(_('No internal transfer picking type found for this company.'))

        created_picking_ids = []
        for dest_loc, lines in location_group.items():
            picking_vals = {
                'picking_type_id': picking_type.id,
                'location_id': self.picking_id.location_dest_id.id,
                'location_dest_id': dest_loc.id,
                'origin': self.picking_id.name,
                'partner_id': self.picking_id.partner_id.id,
                'move_ids': [],
            }
            
            for line in lines:
                picking_vals['move_ids'].append((0, 0, {
                    'description_picking': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty_to_distribute,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': self.picking_id.location_dest_id.id,
                    'location_dest_id': dest_loc.id,
                }))
                
            new_picking = self.env['stock.picking'].create(picking_vals)
            new_picking.action_confirm()
            new_picking.action_assign()
            created_picking_ids.append(new_picking.id)

        if created_picking_ids:
            return {
                'name': _('Distributed Pickings'),
                'view_mode': 'list,form',
                'res_model': 'stock.picking',
                'domain': [('id', 'in', created_picking_ids)],
                'type': 'ir.actions.act_window',
            }

class WizardReceiptDistributeLine(models.TransientModel):
    _name = 'wizard.receipt.distribute.line'
    _description = 'Receipt Distribution Line'

    wizard_id = fields.Many2one('wizard.receipt.distribute', string='Wizard')
    move_id = fields.Many2one('stock.move', string='Receipt Line', required=True)
    product_id = fields.Many2one('product.product', related='move_id.product_id', string='Product')
    qty_to_distribute = fields.Float(string='Quantity')
    dest_location_id = fields.Many2one('stock.location', string='Destination Location', domain="[('usage', '=', 'internal')]")
