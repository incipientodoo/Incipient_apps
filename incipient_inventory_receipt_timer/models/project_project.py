from odoo import fields, models

class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_receipt_timer_project = fields.Boolean(
        string='Use for Receipt Timers',
        help="If checked, this project will be used to auto-provision tasks when starting receipt timers."
    )
