from odoo import models, api, fields
from markupsafe import Markup

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def button_finish(self):
        res = super(MrpWorkorder, self).button_finish()
        for wo in self:
            if not wo.production_id:
                continue
            
            # Start linked workcenters
            if wo.workcenter_id.auto_start_workcenter_ids:
                start_wos = wo.production_id.workorder_ids.filtered(
                    lambda w: w.workcenter_id in wo.workcenter_id.auto_start_workcenter_ids and w.state in ('ready', 'pending')
                )
                if start_wos:
                    start_wos.button_start()
                    for sw in start_wos:
                        wo.production_id.message_post(
                            body=Markup(
                                f"🚀 <b>Auto Chaining:</b> Work Order <b>{sw.name}</b> on Work Center "
                                f"<b>{sw.workcenter_id.name}</b> has been <b>automatically started</b> "
                                f"(triggered by completion of <b>{wo.name}</b> on <b>{wo.workcenter_id.name}</b>)."
                            ),
                            subtype_xmlid='mail.mt_note',
                        )

            # Stop linked workcenters (pause/pending)
            if wo.workcenter_id.auto_stop_workcenter_ids:
                stop_wos = wo.production_id.workorder_ids.filtered(
                    lambda w: w.workcenter_id in wo.workcenter_id.auto_stop_workcenter_ids and w.state == 'progress'
                )
                if stop_wos:
                    stop_wos.button_pending()
                    for stw in stop_wos:
                        wo.production_id.message_post(
                            body=Markup(
                                f"⏸️ <b>Auto Chaining:</b> Work Order <b>{stw.name}</b> on Work Center "
                                f"<b>{stw.workcenter_id.name}</b> has been <b>automatically stopped / paused</b> "
                                f"(triggered by completion of <b>{wo.name}</b> on <b>{wo.workcenter_id.name}</b>)."
                            ),
                            subtype_xmlid='mail.mt_note',
                        )
                    
        return res

    @api.model
    def _cron_auto_finish_workorders(self):
        """ Auto finish workorders that exceed their expected duration """
        now = fields.Datetime.now()
        # Find in-progress workorders on workcenters that have auto-finish enabled
        progress_wos = self.sudo().search([
            ('state', '=', 'progress'),
            ('workcenter_id.auto_finish_workorder', '=', True),
            ('date_start', '!=', False)
        ])
        for wo in progress_wos:
            if not wo.duration_expected:
                continue
            
            # Calculate when the WO was supposed to be finished
            expected_end_time = fields.Datetime.add(wo.date_start, minutes=wo.duration_expected)
            if now >= expected_end_time:
                # Close open timers with expected_end_time so cron polling latency doesn't inflate duration
                open_timers = self.env['mrp.workcenter.productivity'].search([
                    ('workorder_id', '=', wo.id),
                    ('date_end', '=', False)
                ])
                if open_timers:
                    open_timers.write({'date_end': expected_end_time})

                wo.button_finish()

                if wo.production_id:
                    wo.production_id.message_post(
                        body=Markup(
                            f"⏱️ <b>Auto Finish:</b> Work Order <b>{wo.name}</b> on Work Center "
                            f"<b>{wo.workcenter_id.name}</b> was <b>automatically finished</b> by cron "
                            f"as expected duration ({wo.duration_expected:.2f} min) elapsed."
                        ),
                        subtype_xmlid='mail.mt_note',
                    )
