from odoo import models, fields, api
import calendar, re


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()

        for production in self:
            if production.date_start:
                # Setting date finished supaya sama dengan date start
                production.date_finished = production.date_start
                
                moves = self.env['account.move'].search([
                    ('stock_move_id', 'in', production.move_finished_ids.ids)
                ])
                picking_type_code = production.picking_type_id.sequence_code or 'XXXXX'

                for move in moves:
                    if move.state == 'posted':
                        move.button_draft()

                    move.name = False
                    move.date = production.date_start.date()

                    move_year = move.date.year % 100
                    move_month = move.date.month

                    sequence = 1
                    while True:
                        new_name = f"STJ/{picking_type_code} {move_year}/{move_month:02d}/{sequence:05d}"
                        existing = self.env['account.move'].search([('name', '=', new_name)], limit=1)
                        if not existing:
                            break
                        sequence += 1

                    move.name = new_name
                    move._compute_name()

                    if move.state == 'draft':
                        move.action_post()

                for move_line in production.move_raw_ids:
                    if move_line.date:
                        move_line.date = production.date_start.date()

                    account_moves = self.env['account.move'].search([
                        ('stock_move_id', '=', move_line.id)
                    ])

                    for account_move in account_moves:
                        if account_move.state == 'posted':
                            account_move.button_draft()

                        account_move.name = False
                        account_move.date = production.date_start.date()

                        move_year = account_move.date.year % 100
                        move_month = account_move.date.month

                        sequence = 1
                        while True:
                            new_name = f"STJ/{picking_type_code} {move_year}/{move_month:02d}/{sequence:05d}"
                            existing = self.env['account.move'].search([('name', '=', new_name)], limit=1)
                            if not existing:
                                break
                            sequence += 1

                        account_move.name = new_name
                        account_move._compute_name()

                        if account_move.state == 'draft':
                            account_move.action_post()
        return res
