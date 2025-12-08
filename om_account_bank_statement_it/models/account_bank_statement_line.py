from odoo import models, fields, api, SUPERUSER_ID
import logging
import re

_logger = logging.getLogger(__name__)

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    initial_date = fields.Date(string="Initial Date", help="Menyimpan tanggal awal sebelum diubah")

    @api.model
    def _get_next_sequence(self, year, month, journal):
        """Menghasilkan nomor urut (5 digit) berdasarkan tahun & bulan untuk journal"""

        prefix = f"{journal.code} {year}/{month}/"
        # Query untuk ambil nomor urut terakhir dengan parsing di SQL
        self.env.cr.execute("""
            SELECT name FROM account_move
            WHERE name LIKE %s AND journal_id = %s
            ORDER BY RIGHT(name, 5)::int DESC
            LIMIT 1
            FOR UPDATE
        """, (f"{prefix}%", journal.id))

        last_request = self.env.cr.fetchone()
        last_name = str(last_request[0]) if last_request and last_request[0] else None

        _logger.info(f"Last request found: {last_name if last_name else 'None'}")

        if last_name:
            # Regex untuk ambil 5 digit terakhir
            match = re.match(rf"{re.escape(prefix)}(\d{{5}})$", last_name)
            if match:
                try:
                    last_number = int(match.group(1))
                    _logger.info(f"Last number parsed: {last_number}")
                    next_number = f"{last_number + 1:05d}"
                    _logger.info(f"Next sequence generated: {next_number}")
                    return next_number
                except ValueError:
                    _logger.warning(f"Gagal parsing nomor urut dari {last_name}")

        _logger.info("Returning default sequence: 00001")
        return "00001"

    def _get_custom_sequence(self, date, journal):
        """Generate sequence hanya untuk journal yang mengandung cash dan bank"""

        if not journal or journal.type not in ('bank', 'cash'):
            return False

        year = date.strftime("%y")
        month = date.strftime("%m")
        sequence_number = self._get_next_sequence(year, month, journal)
        prefix = f"{journal.code}"
        return f"{prefix} {year}/{month}/{sequence_number}"

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info(f"Creating records with values: {vals_list}")
        st_lines = super().create(vals_list)

        for st_line in st_lines:
            journal = st_line.journal_id
            if journal.type in ('bank', 'cash') and st_line.date:
                st_line.initial_date = st_line.date
                _logger.info(f"Processing record {st_line.id} with initial date {st_line.initial_date}")

                # Pastikan move_id ada dan journal sama, serta name belum sesuai format
                if st_line.move_id and st_line.move_id.journal_id.id == journal.id:
                    expected_prefix = f"{journal.code} {st_line.initial_date.strftime('%y')}/{st_line.initial_date.strftime('%m')}/"
                    if not st_line.move_id.name or not st_line.move_id.name.startswith(expected_prefix):
                        custom_sequence = self._get_custom_sequence(st_line.initial_date, journal)
                        _logger.info(f"Updating account_move {st_line.move_id.id} with name={custom_sequence} and date={st_line.initial_date}")

                        if st_line.move_id.state == 'posted':
                            st_line.move_id.sudo().button_draft()

                        st_line.move_id.sudo().write({'name': custom_sequence, 'date': st_line.initial_date})
                        st_line.move_id.sudo().action_post()

        return st_lines

    def write(self, vals):
        _logger.info(f"Updating records {self.ids} with values: {vals}")

        if 'date' in vals:
            for record in self:
                journal = record.journal_id
                if record.journal_id.type in ('bank', 'cash'):  # Hanya journal type bank dan cash yang diproses
                    old_date = record.date
                    new_date = vals['date']
                    _logger.info(f"Record {record.id} changing date from {old_date} to {new_date}")

                    # Jika tanggal tidak berubah, lewati
                    if old_date == new_date:
                        _logger.info(f"Skipping sequence update for record {record.id} because date is unchanged")
                        continue

                    record.initial_date = new_date
                    new_sequence = self._get_custom_sequence(new_date, journal)

                    if record.move_id and record.move_id.journal_id.id == journal.id:
                        _logger.info(
                            f"Updating account_move {record.move_id.id} with name={new_sequence} and date={new_date}")
                        if record.move_id.state == 'posted':
                            record.move_id.sudo().button_draft()
                        record.move_id.sudo().write({'name': new_sequence, 'date': new_date})
                        record.move_id.sudo().action_post()

        return super().write(vals)

    def _update_sequence(self):
        """Update move sequence and date based on initial_date and journal type"""
        for record in self:
            journal = record.journal_id
            if journal.type in ('bank', 'cash') and record.move_id and record.initial_date:
                custom_sequence = self._get_custom_sequence(record.initial_date, journal)
                if custom_sequence:
                    if record.move_id.state == 'posted':
                        record.move_id.sudo().button_draft()
                    record.move_id.sudo().write({'name': custom_sequence, 'date': record.initial_date})
                    record.move_id.sudo().action_post()
    
    def action_save_close(self):
        _logger.info(f"Executing action_save_close for records {self.ids}")
        self._update_sequence()
        return {'type': 'ir.actions.act_window_close'}

    def action_save_new(self):
        _logger.info(f"Executing action_save_new for records {self.ids}")
        self._update_sequence()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'account_accountant.action_bank_statement_line_form_bank_rec_widget'
        )
        action['context'] = {'default_journal_id': self._context.get('default_journal_id')}
        return action
    