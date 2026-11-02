# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ArchiveOperationsWizard(models.TransientModel):
    _name = 'mrp.routing.archive.wizard'
    _description = 'Wizard to Bulk Archive Operations and Cleanup Orphans'

    operation_ids = fields.Many2many(
        'mrp.routing.workcenter',
        string='Operations to Archive',
        required=True
    )

    @api.model
    def default_get(self, fields_list):
        res = super(ArchiveOperationsWizard, self).default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model')
        if active_model == 'mrp.routing.workcenter' and active_ids:
            res['operation_ids'] = [(6, 0, active_ids)]
        return res

    def action_archive_and_cleanup(self):
        self.ensure_one()
        if not self.operation_ids:
            return {'type': 'ir.actions.act_window_close'}

        operations = self.operation_ids

        # 1. Archive the selected operations
        operations.write({'active': False})

        # 2. Find and archive orphaned quality points linked to these operations
        quality_points = self.env['quality.point'].sudo().search([
            ('operation_id', 'in', operations.ids)
        ])
        
        if quality_points:
            quality_points.write({'active': False})

        return {'type': 'ir.actions.act_window_close'}
