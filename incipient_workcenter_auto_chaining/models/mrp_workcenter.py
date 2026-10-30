from odoo import models, fields

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    auto_start_workcenter_ids = fields.Many2many(
        'mrp.workcenter',
        'mrp_workcenter_auto_start_rel',
        'workcenter_id',
        'linked_workcenter_id',
        string="Auto-Start Workcenters",
        help="When an operation on this workcenter is finished, work orders on these linked workcenters for the same MO will automatically start."
    )
    
    auto_stop_workcenter_ids = fields.Many2many(
        'mrp.workcenter',
        'mrp_workcenter_auto_stop_rel',
        'workcenter_id',
        'linked_workcenter_id',
        string="Auto-Stop Workcenters",
        help="When an operation on this workcenter is finished, work orders on these linked workcenters for the same MO will automatically pause/stop."
    )

    auto_finish_workorder = fields.Boolean(
        string="Auto-Finish by Cron",
        default=False,
        help="If enabled, a scheduled action will automatically finish work orders on this workcenter once their expected duration elapses."
    )
