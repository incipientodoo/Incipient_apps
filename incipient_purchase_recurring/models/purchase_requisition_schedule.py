from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date

class PurchaseRequisitionScheduleLine(models.Model):
    _name = 'purchase.requisition.schedule.line'
    _description = 'Blanket Agreement Scheduled PO Line'
    _order = 'date_scheduled asc, id asc'

    requisition_id = fields.Many2one(
        'purchase.requisition',
        string='Blanket Agreement',
        required=True,
        ondelete='cascade'
    )
    date_scheduled = fields.Date(
        string='Scheduled Date',
        required=True
    )
    state = fields.Selection([
        ('draft', 'Scheduled'),
        ('generated', 'PO Created'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status', required=True)

    purchase_id = fields.Many2one(
        'purchase.order',
        string='Generated Purchase Order',
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        related='requisition_id.company_id',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='requisition_id.currency_id'
    )

    def action_generate_po(self):
        for line in self:
            if line.state == 'generated' and line.purchase_id:
                continue
            req = line.requisition_id
            vendor = req.vendor_id
            if not vendor:
                raise UserError(_('Please set a Vendor on Blanket Order %s before generating scheduled POs.') % req.name)

            po_vals = {
                'partner_id': vendor.id,
                'requisition_id': req.id,
                'company_id': req.company_id.id,
                'currency_id': req.currency_id.id,
                'user_id': req.user_id.id or self.env.uid,
                'origin': _('%s (Scheduled: %s)') % (req.name, line.date_scheduled),
                'order_line': [],
            }
            for req_line in req.line_ids:
                po_vals['order_line'].append((0, 0, {
                    'product_id': req_line.product_id.id,
                    'product_qty': req_line.product_qty or 1.0,
                    'price_unit': req_line.price_unit,
                    'product_uom_id': req_line.product_uom_id.id if hasattr(req_line, 'product_uom_id') else req_line.product_id.uom_po_id.id,
                    'name': req_line.product_id.display_name,
                    'date_planned': fields.Datetime.now(),
                }))

            po = self.env['purchase.order'].create(po_vals)
            line.write({
                'purchase_id': po.id,
                'state': 'generated',
            })
            req.message_post(body=_('Scheduled Purchase Order <b>%s</b> generated automatically for date %s.') % (po.name, line.date_scheduled))
        return True


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    schedule_line_ids = fields.One2many(
        'purchase.requisition.schedule.line',
        'requisition_id',
        string='Scheduled PO Releases'
    )
    scheduled_po_count = fields.Integer(
        compute='_compute_scheduled_po_count',
        string='Scheduled PO Releases Count'
    )

    @api.depends('schedule_line_ids')
    def _compute_scheduled_po_count(self):
        for req in self:
            req.scheduled_po_count = len(req.schedule_line_ids)

    def action_open_schedule_wizard(self):
        self.ensure_one()
        if self.date_end:
            default_end_date = self.date_end if isinstance(self.date_end, date) else self.date_end.date()
        else:
            default_end_date = fields.Date.today() + relativedelta(months=6)

        return {
            'name': _('Generate Recurring PO Schedule'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition.schedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_requisition_id': self.id,
                'default_start_date': fields.Date.today(),
                'default_end_date': default_end_date,
            }
        }

    def cron_generate_scheduled_purchase_orders(self):
        today = fields.Date.today()
        lines = self.env['purchase.requisition.schedule.line'].search([
            ('date_scheduled', '<=', today),
            ('state', '=', 'draft'),
            ('requisition_id.state', 'not in', ['cancel', 'closed', 'done'])
        ])
        for line in lines:
            try:
                line.action_generate_po()
            except Exception as e:
                line.requisition_id.message_post(body=_('Failed to auto-generate scheduled PO for date %s: %s') % (line.date_scheduled, str(e)))


class PurchaseRequisitionScheduleWizard(models.TransientModel):
    _name = 'purchase.requisition.schedule.wizard'
    _description = 'Generate Recurring Purchase Schedule Wizard'

    requisition_id = fields.Many2one(
        'purchase.requisition',
        string='Blanket Agreement',
        required=True
    )
    start_date = fields.Date(
        string='Schedule Start Date',
        required=True,
        default=fields.Date.context_today
    )
    end_date = fields.Date(
        string='Schedule End Date',
        required=True
    )
    period_num = fields.Integer(
        string='Every N',
        default=1,
        required=True
    )
    period_unit = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ], default='months', string='Recurrence Unit', required=True)

    def action_generate_schedule(self):
        self.ensure_one()
        if self.period_num <= 0:
            raise UserError(_('Recurrence period number must be greater than 0.'))
        if self.start_date > self.end_date:
            raise UserError(_('Start date cannot be after End date.'))

        curr_date = self.start_date
        created_lines = self.env['purchase.requisition.schedule.line']

        while curr_date <= self.end_date:
            existing = self.env['purchase.requisition.schedule.line'].search([
                ('requisition_id', '=', self.requisition_id.id),
                ('date_scheduled', '=', curr_date)
            ], limit=1)
            if not existing:
                line = self.env['purchase.requisition.schedule.line'].create({
                    'requisition_id': self.requisition_id.id,
                    'date_scheduled': curr_date,
                    'state': 'draft',
                })
                created_lines |= line

            if self.period_unit == 'days':
                curr_date += relativedelta(days=self.period_num)
            elif self.period_unit == 'weeks':
                curr_date += relativedelta(weeks=self.period_num)
            elif self.period_unit == 'months':
                curr_date += relativedelta(months=self.period_num)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Schedule Generated'),
                'message': _('%d scheduled PO releases created.') % len(created_lines),
                'sticky': False,
            }
        }
