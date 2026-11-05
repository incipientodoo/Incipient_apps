from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_timer_running = fields.Boolean(
        string="Timer Running", 
        compute='_compute_is_timer_running', 
        search='_search_is_timer_running'
    )
    timer_start_time = fields.Datetime(string="Timer Start Time")
    project_task_id = fields.Many2one('project.task', string="Linked Task", copy=False)
    active_timer_user_id = fields.Many2one('res.users', string="Active Timer User", copy=False)
    
    timesheet_ids = fields.One2many(related='project_task_id.timesheet_ids', string="Timesheets")
    timesheet_count = fields.Integer(compute='_compute_timesheet_count')

    @api.depends('active_timer_user_id')
    def _compute_is_timer_running(self):
        for picking in self:
            picking.is_timer_running = picking.active_timer_user_id == self.env.user

    def _search_is_timer_running(self, operator, value):
        if operator == '=':
            if value:
                return [('active_timer_user_id', '=', self.env.user.id)]
            else:
                return [('active_timer_user_id', '!=', self.env.user.id)]
        elif operator == '!=':
            if value:
                return [('active_timer_user_id', '!=', self.env.user.id)]
            else:
                return [('active_timer_user_id', '=', self.env.user.id)]
        raise NotImplementedError("Unsupported operator for is_timer_running")

    @api.depends('timesheet_ids')
    def _compute_timesheet_count(self):
        for picking in self:
            picking.timesheet_count = len(picking.timesheet_ids)

    def action_start_timer(self):
        self.ensure_one()
        if self.env.user.active_receipt_timer_id:
            raise UserError(_("You already have an active timer running on receipt %s. Please stop it first.", self.env.user.active_receipt_timer_id.name))
            
        if self.active_timer_user_id:
            raise UserError(_("Another user (%s) is already processing this receipt.", self.active_timer_user_id.name))
        
        if not self.project_task_id:
            project = self.env['project.project'].search([
                ('is_receipt_timer_project', '=', True),
                '|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)
            ], limit=1)
            if not project:
                raise UserError(_("Please configure at least one 'Use for Receipt Timers' project in the Project app settings."))
            
            task = self.env['project.task'].sudo().create({
                'name': _('Processing %s', self.name),
                'project_id': project.id,
                'company_id': self.company_id.id,
                'partner_id': self.partner_id.id,
                'description': _('Auto-provisioned task for receipt %s', self.name),
            })
            self.project_task_id = task.id
        
        self.write({
            'timer_start_time': fields.Datetime.now(),
            'active_timer_user_id': self.env.user.id,
        })
        self.env.user.sudo().active_receipt_timer_id = self.id
        return True

    def action_stop_timer(self):
        self.ensure_one()
        if not self.is_timer_running or self.active_timer_user_id != self.env.user:
            raise UserError(_("You do not have an active timer for this receipt."))
        
        start_time = self.timer_start_time
        stop_time = fields.Datetime.now()
        
        if start_time:
            delta = stop_time - start_time
            hours = delta.total_seconds() / 3600.0
            
            if hours > 0:
                employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
                if not employee:
                    raise UserError(_("You need to have an employee record linked to your user to log timesheets."))
                
                self.env['account.analytic.line'].sudo().create({
                    'name': _('Receipt %s processing', self.name),
                    'project_id': self.project_task_id.project_id.id,
                    'task_id': self.project_task_id.id,
                    'unit_amount': hours,
                    'employee_id': employee.id,
                    'company_id': self.company_id.id,
                })
        
        self.write({
            'timer_start_time': False,
            'active_timer_user_id': False,
        })
        self.env.user.sudo().active_receipt_timer_id = False
        return True
        
    def action_view_timesheets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Timesheets'),
            'domain': [('task_id', '=', self.project_task_id.id)],
            'res_model': 'account.analytic.line',
            'view_mode': 'list,form',
            'context': {
                'default_task_id': self.project_task_id.id, 
                'default_project_id': self.project_task_id.project_id.id
            },
        }
        
    def action_view_task(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Linked Task'),
            'res_model': 'project.task',
            'res_id': self.project_task_id.id,
            'view_mode': 'form',
        }
