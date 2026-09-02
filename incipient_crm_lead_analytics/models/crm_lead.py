# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    lead_age_bucket = fields.Char(string="Lead Age Bucket")
    cycle_time_to_qualify = fields.Integer(
        string="Cycle Time (Days) to Qualify",
        compute="_compute_cycle_time_to_qualify",
        readonly=True, store=True
    )
    forecast_bucket = fields.Char(string="Forecast Bucket", readonly=True)
    lead_to_opp_bucket = fields.Selection(
        selection=[
            ("90_plus_days", "> 90 Days"),
            ("last_90_days", "< 90 Days"),
            ("last_60_days", "< 60 Days"),
            ("last_30_days", "< 30 Days"),
            ("last_15_days", "< 15 Days"),
        ], string="Lead to Opp Bucket", readonly=True
    )
    neglected_status = fields.Boolean(string='Neglected Status', readonly=True, default=False)
    
    last_sales_step = fields.Char(string="Last Sales Step", compute="_compute_sales_steps", store=True)
    last_sales_step_date = fields.Date(string="Last Sales Step Date", compute="_compute_sales_steps", store=True)
    next_sales_step = fields.Char(string="Next Sales Step", compute="_compute_sales_steps", store=True)
    next_sales_step_date = fields.Date(string="Next Sales Step Date", compute="_compute_sales_steps", store=True)

    @api.depends('activity_ids', 'activity_ids.state', 'activity_ids.date_deadline')
    def _compute_sales_steps(self):
        mail_obj = self.env['mail.message']
        for lead in self:
            last_done_activity = mail_obj.search([
                ('model', '=', 'crm.lead'),
                ('res_id', '=', lead.id),
                ('mail_activity_type_id', '!=', False),
                ('subtype_id.internal', '=', True),
            ], order='id desc', limit=1)

            planned_activities = lead.activity_ids.filtered(
                lambda act: act.state != 'done'
            ).sorted(
                key=lambda act: act.date_deadline or fields.Date.today()
            )

            if last_done_activity:
                lead.last_sales_step = last_done_activity.mail_activity_type_id.name
                lead.last_sales_step_date = last_done_activity.date
            else:
                lead.last_sales_step = False
                lead.last_sales_step_date = False

            if planned_activities:
                next_activity = planned_activities[0]
                lead.next_sales_step = next_activity.activity_type_id.name
                lead.next_sales_step_date = next_activity.date_deadline
            else:
                lead.next_sales_step = False
                lead.next_sales_step_date = False

    @api.depends('date_conversion', 'create_date')
    def _compute_cycle_time_to_qualify(self):
        for lead in self:
            cycle_time = 0
            if lead.date_conversion and lead.create_date:
                cycle_time = (lead.date_conversion.date() - lead.create_date.date()).days
            lead.cycle_time_to_qualify = cycle_time

    @api.constrains('date_deadline')
    def _check_date_deadline(self):
        if self.env.context.get('install_mode_data'):
            return
        for record in self:
            if record.date_deadline and record.create_date:
                if record.date_deadline <= record.create_date.date():
                    raise ValidationError(_('Expected closing date must be greater than the creation date...'))

    def _cron_update_neglected_status(self):
        today = fields.Date.today()
        limit_date = today - timedelta(days=10)

        neglected_domain = [
            ('active', '=', True),
            ('stage_id.is_won', '=', False),
            '|',
                ('last_sales_step_date', '<', limit_date),
                '&', ('last_sales_step_date', '=', False), ('create_date', '<', limit_date),
            '|',
                ('next_sales_step_date', '=', False),
                ('next_sales_step_date', '<', limit_date)
        ]

        records_to_neglect = self.search(neglected_domain + [('neglected_status', '=', False)])
        if records_to_neglect:
            records_to_neglect.write({'neglected_status': True})

        to_unneglect_domain = [('neglected_status', '=', True), '!', *neglected_domain]
        records_to_unneglect = self.search(to_unneglect_domain)
        if records_to_unneglect:
            records_to_unneglect.write({'neglected_status': False})

    def _cron_update_buckets(self):
        for pipeline in self.search([]):
            if pipeline.date_deadline and pipeline.create_date:
                closing_days = (pipeline.date_deadline - pipeline.create_date.date()).days
                if closing_days > 90:
                    pipeline.forecast_bucket = '> 90 Days'
                elif closing_days > 60:
                    pipeline.forecast_bucket = '< 90 Days'
                elif closing_days > 30:
                    pipeline.forecast_bucket = '< 60 Days'
                elif closing_days > 15:
                    pipeline.forecast_bucket = '< 30 Days'
                else:
                    pipeline.forecast_bucket = '< 15 Days'
            else:
                pipeline.forecast_bucket = False

            if pipeline.date_conversion and pipeline.create_date:
                lead_to_opp_time_days = (pipeline.date_conversion - pipeline.create_date).days
                if lead_to_opp_time_days > 90:
                    pipeline.lead_to_opp_bucket = '90_plus_days'
                elif lead_to_opp_time_days > 60:
                    pipeline.lead_to_opp_bucket = 'last_90_days'
                elif lead_to_opp_time_days > 30:
                    pipeline.lead_to_opp_bucket = 'last_60_days'
                elif lead_to_opp_time_days > 15:
                    pipeline.lead_to_opp_bucket = 'last_30_days'
                else:
                    pipeline.lead_to_opp_bucket = 'last_15_days'
            else:
                pipeline.lead_to_opp_bucket = False

            if pipeline.create_date:
                lead_age_days = (datetime.today().date() - pipeline.create_date.date()).days
                if lead_age_days > 90:
                    pipeline.lead_age_bucket = "> 90 Days"
                elif lead_age_days > 60:
                    pipeline.lead_age_bucket = "< 90 Days"
                elif lead_age_days > 30:
                    pipeline.lead_age_bucket = "< 60 Days"
                elif lead_age_days > 15:
                    pipeline.lead_age_bucket = "< 30 Days"
                else:
                    pipeline.lead_age_bucket = "< 15 Days"
            else:
                pipeline.lead_age_bucket = "Undefined"
