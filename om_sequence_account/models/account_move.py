# -*- coding: utf-8 -*-

from odoo import models, fields, api
import re

class AccountMove(models.Model):
    _inherit = 'account.move'

    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence',
        copy=False, check_company=True)

    @api.depends('posted_before', 'state', 'journal_id', 'date', 'move_type', 'origin_payment_id')
    def _compute_name(self):
        self = self.sorted(lambda m: (m.date, m.ref or '', m._origin.id))

        for move in self:
            if move.state == 'cancel':
                continue

            move_has_name = move.name and move.name != '/'
            if not move.posted_before and not move._sequence_matches_date():
                # The name does not match the date and the move is not the first in the period:
                # Reset to draft
                move.name = False
                continue
            if move.date and not move_has_name and move.state != 'draft':
                # move._set_next_sequence()
                
               
                if self.journal_id.sequence_id:
                    date = self.date if self.journal_id.type == 'general' else self.invoice_date
                    seq_date = fields.Datetime.context_timestamp(
                        self, fields.Datetime.to_datetime(date)
                        ) if date else None
                    
                    move.name = self.journal_id.sequence_id.next_by_id(sequence_date=seq_date)
                else:
                    move._set_next_sequence()
            # if not move_has_name and move.state == 'draft':
            #     move._set_next_sequence()

        self._inverse_name()

    # def _get_starting_sequence(self):
    #     res = super(AccountMove, self)._get_starting_sequence()
    #     year_part = "%04d" % self.date.year
    #     last_day = int(self.company_id.fiscalyear_last_day)
    #     last_month = int(self.company_id.fiscalyear_last_month)
    #     year_part = "%04d" % self.date.year
    #     is_staggered_year = last_month != 12 or last_day != 31
    #     if self.journal_id.type in ['sale']:
    #         # res = "%s/%s/%02d/0000" % (self.journal_id.code, year_part, self.date.month)
    #         res = self.env['ir.sequence'].with_company(self.company_id).next_by_code(
    #                     'si.sequence',
    #                     sequence_date=self.date,
    #                 )
    #     if self.journal_id.type in ['purchase']:
    #         # res = "%s/%s/%02d/0000" % (self.journal_id.code, year_part, self.date.month)
    #         res = self.env['ir.sequence'].with_company(self.company_id).next_by_code(
    #                     'pi.sequence',
    #                     sequence_date=self.date,
    #                 )
    #     return res
    
    def _get_sequence_format_param(self, previous):
        """Get the python format and format values for the sequence.

        :param previous: the sequence we want to extract the format from
        :return tuple(format, format_values):
            format is the format string on which we should call .format()
            format_values is the dict of values to format the `format` string
            ``format.format(**format_values)`` should be equal to ``previous``
        """
        sequence_number_reset = self._deduce_sequence_number_reset(previous)
        # regex = self._sequence_fixed_regex
        regex = r'(?P<prefix1>\w+/\w+)\s(?P<year>\d{2})/(?P<month>\d{2})/(?P<seq>\d+)$'
        if sequence_number_reset == 'year':
            regex = self._sequence_yearly_regex
        elif sequence_number_reset == 'year_range':
            regex = self._sequence_year_range_regex
        elif sequence_number_reset == 'month':
            regex = self._sequence_monthly_regex
        elif sequence_number_reset == 'year_range_month':
            regex = self._sequence_year_range_monthly_regex
        format_values = re.match(regex, previous).groupdict()
        # format_values['seq_length'] = len(format_values['seq'])
        format_values['seq_length'] = 5
        format_values['year'] = int(str(self.date.year)[-2:]) if self.date else int(str(format_values['year'])[-2:])
        # format_values['year_length'] = len(format_values.get('year') or '')
        format_values['year_length'] = 2
        format_values['year_end_length'] = len(format_values.get('year_end') or '')
        if not format_values.get('seq') and 'prefix1' in format_values and 'suffix' in format_values:
            # if we don't have a seq, consider we only have a prefix and not a suffix
            format_values['prefix1'] = format_values['suffix']
            format_values['suffix'] = ''
        for field in ('seq', 'year', 'month', 'year_end'):
            format_values[field] = int(format_values.get(field) or 0)

        if self.journal_id.code == 'STJ' and self.ref:
            ref = self.ref.split(' - ')[0]
            stock = self.env['stock.picking'].search([('name', '=', ref)], limit=1)
            format_values['prefix1'] = format_values['prefix1'].split('/')[0].strip() + '/' # Riset Format
            if stock and stock.picking_type_id.code == 'outgoing':
                # format_values['prefix1'] = format_values['prefix1'].split('/')[0] + '/' + 'DO/'
                format_values['prefix1'] += 'DO '  # Jika outgoing
            if stock and stock.picking_type_id.code == 'incoming':
                # format_values['prefix1'] = format_values['prefix1'] + 'TTB/'
                # format_values['prefix1']= format_values['prefix1'].split('/')[0] + '/' + 'TTB/'
                format_values['prefix1'] += 'TTB '  # Jika incoming
            mo = self.env['mrp.production'].search([('name', '=', ref)], limit=1)
            if mo:
                # format_values['prefix1'] = format_values['prefix1'] + 'PBP/'
                # format_values['prefix1'] = format_values['prefix1'].split('/')[0] + '/' + 'PBP/'
                format_values['prefix1'] += 'PBP '  # Jika produksi

        placeholders = re.findall(r'\b(prefix\d|seq|suffix\d?|year|year_end|month)\b', regex)
        format = ''.join(
            "{seq:0{seq_length}d}" if s == 'seq' else
            "{month:02d}" if s == 'month' else
            "{year:0{year_length}d}" if s == 'year' else
            "{year_end:0{year_end_length}d}" if s == 'year_end' else
            "{%s}" % s
            for s in placeholders
        )
        return format, format_values
