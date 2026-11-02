# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountInternalTransferEngine(models.Model):
    _name = 'account.internal.transfer.engine'
    _description = 'Internal Bank/Cash Transfer Engine'
    _order = 'date desc, id desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled')
    ], string='Status', required=True, readonly=True, copy=False, default='draft')
    
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
    
    source_journal_id = fields.Many2one('account.journal', string='Source Journal', required=True, domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")
    destination_journal_id = fields.Many2one('account.journal', string='Destination Journal', required=True, domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")
    
    transit_account_id = fields.Many2one('account.account', string='Transit Account', required=True, domain="[('company_ids', 'in', company_id)]",
                                         help="The account used to temporarily hold funds during the transfer.")
    
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    memo = fields.Char(string='Memo')
    
    move_ids = fields.Many2many('account.move', string='Journal Entries', readonly=True, copy=False)

    @api.constrains('source_journal_id', 'destination_journal_id')
    def _check_journals(self):
        for record in self:
            if record.source_journal_id == record.destination_journal_id:
                raise ValidationError(_("Source and Destination journals must be different."))

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_("The transfer amount must be strictly positive."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].sudo().next_by_code('account.internal.transfer.engine') or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft transfers can be confirmed."))
            
        source_account = self.source_journal_id.default_account_id
        if not source_account:
            raise UserError(_("Please define a default account on the source journal."))
            
        dest_account = self.destination_journal_id.default_account_id
        if not dest_account:
            raise UserError(_("Please define a default account on the destination journal."))

        move_vals_list = []
        
        # 1. Entry for Source Journal (Credit Bank, Debit Transit)
        move1_lines = [
            (0, 0, {
                'name': self.memo or _('Internal Transfer'),
                'account_id': self.transit_account_id.id,
                'debit': self.amount,
                'credit': 0.0,
            }),
            (0, 0, {
                'name': self.memo or _('Internal Transfer'),
                'account_id': source_account.id,
                'debit': 0.0,
                'credit': self.amount,
            })
        ]
        move_vals_list.append({
            'journal_id': self.source_journal_id.id,
            'date': self.date,
            'ref': self.name,
            'line_ids': move1_lines,
        })
        
        # 2. Entry for Destination Journal (Credit Transit, Debit Bank)
        move2_lines = [
            (0, 0, {
                'name': self.memo or _('Internal Transfer'),
                'account_id': dest_account.id,
                'debit': self.amount,
                'credit': 0.0,
            }),
            (0, 0, {
                'name': self.memo or _('Internal Transfer'),
                'account_id': self.transit_account_id.id,
                'debit': 0.0,
                'credit': self.amount,
            })
        ]
        move_vals_list.append({
            'journal_id': self.destination_journal_id.id,
            'date': self.date,
            'ref': self.name,
            'line_ids': move2_lines,
        })
        
        moves = self.env['account.move'].sudo().create(move_vals_list)
        moves.sudo().action_post()
        
        self.write({
            'state': 'confirm',
            'move_ids': [(6, 0, moves.ids)]
        })

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state not in ('confirm', 'cancel'):
            raise UserError(_("Cannot reset to draft from the current state."))
            
        # Reverse/Cancel moves
        if self.move_ids:
            for move in self.move_ids:
                if move.state == 'posted':
                    move.button_draft()
                if move.state == 'draft':
                    move.button_cancel()
        
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.ensure_one()
        if self.move_ids:
            for move in self.move_ids:
                if move.state == 'posted':
                    move.button_draft()
                if move.state == 'draft':
                    move.button_cancel()
        self.write({'state': 'cancel'})
