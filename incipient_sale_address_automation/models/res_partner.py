from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    primary_saleable_partner_id = fields.Many2one('res.partner', string="Primary Sales Contact", domain="[('parent_id', '=', id),('parent_id', '!=', False)]")
    primary_account_partner_id = fields.Many2one('res.partner', string="Primary Accounting Contact", domain="[('parent_id', '=', id),('parent_id', '!=', False)]")
    is_primary_account = fields.Boolean(string="Primary Accounting Contact")
    is_primary_saleable = fields.Boolean(string="Primary Sales Contact")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        for record, vals in zip(res, vals_list):
            if record.is_primary_account and record.parent_id:
                record.parent_id.child_ids.filtered(lambda r: r.id != record.id).write({
                    'is_primary_account': False
                })
                record.parent_id.primary_account_partner_id = record.id

            if record.is_primary_saleable and record.parent_id:
                record.parent_id.child_ids.filtered(
                    lambda r: r.id != record.id
                ).write({'is_primary_saleable': False})
                record.parent_id.primary_saleable_partner_id = record.id
            if record.parent_id:
                res.write({'is_company':False})
        return res

    @api.onchange('primary_account_partner_id')
    def _onchange_primary_account_partner_id(self):
        self.child_ids.filtered(lambda r: r.id != self.primary_account_partner_id.id).write({
            'is_primary_account': False
        })
        if self.primary_account_partner_id:
            self.primary_account_partner_id.is_primary_account = True

    @api.onchange('primary_saleable_partner_id')
    def _onchange_primary_saleable_partner_id(self):
        self.child_ids.filtered(lambda r: r.id != self.primary_saleable_partner_id.id).write({
            'is_primary_saleable': False
        })
        if self.primary_saleable_partner_id:
            self.primary_saleable_partner_id.is_primary_saleable = True

    def write(self, vals):
        for record in self:
            if 'is_primary_account' in vals and record.parent_id:
                if vals['is_primary_account']:
                    record.parent_id.child_ids.filtered(lambda r: r.id != record.id).write({
                        'is_primary_account': False
                    })
                    record.parent_id.primary_account_partner_id = record.id
                elif record.parent_id.primary_account_partner_id.id == record.id:
                    record.parent_id.primary_account_partner_id = False
            if 'is_primary_saleable' in vals and record.parent_id:
                if vals['is_primary_saleable']:
                    record.parent_id.child_ids.filtered(lambda r: r.id != record.id).write({
                        'is_primary_saleable': False
                    })
                    record.parent_id.primary_saleable_partner_id = record.id
                elif record.parent_id.primary_saleable_partner_id.id == record.id:
                    record.parent_id.primary_saleable_partner_id = False
                    
        return super(ResPartner, self).write(vals)
