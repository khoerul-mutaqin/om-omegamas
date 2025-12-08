from odoo import _, fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """Override action_post untuk update ke AccountBankStatementLine"""
        for move in self:
            if not move.date:
                raise ValidationError(_("Date is required before posting the journal entry."))

        res = super().action_post()

        for move in self:
            if move.journal_id.id == 208:
                date_obj = move.date or fields.Date.today()
                move.name = self._generate_journal_sequence(date_obj, prefix='JP')
        return res

    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            journal_id = vals.get('journal_id')
            _logger.info(f"[CREATE] start create account.move journal_id={journal_id} ref={vals.get('ref')}")

            # ========== INVENTORY VALUATION (Journal 8) ==========
            if journal_id == 8:
                _logger.info("[CREATE] Journal 8 (Inventory Valuation) detected")
                resolved_date = None
                resolved_prefix = "STJ"

                # 1️⃣ Ambil tanggal dari accounting_date atau invoice_date
                if vals.get('accounting_date'):
                    try:
                        resolved_date = fields.Date.from_string(vals['accounting_date'])
                        _logger.info(f"[CREATE] using vals['accounting_date'] = {resolved_date}")
                    except Exception:
                        resolved_date = None
                elif vals.get('invoice_date'):
                    try:
                        resolved_date = fields.Date.from_string(vals['invoice_date'])
                        _logger.info(f"[CREATE] using vals['invoice_date'] = {resolved_date}")
                    except Exception:
                        resolved_date = None

                # 2️⃣ Ambil stock.move & picking
                stock_move = None
                if vals.get('stock_move_id'):
                    stock_move = self.env['stock.move'].browse(vals['stock_move_id'])
                    if not stock_move.exists():
                        stock_move = None

                stock_picking = None
                if stock_move and stock_move.picking_id:
                    stock_picking = stock_move.picking_id
                elif vals.get('stock_picking_id'):
                    stock_picking = self.env['stock.picking'].browse(vals['stock_picking_id'])
                    if not stock_picking.exists():
                        stock_picking = None

                # 3️⃣ Deteksi Scrap
                scrap = False
                if stock_move:
                    scrap = bool(getattr(stock_move, 'scrap_id', False) or getattr(stock_move, 'scrapped', False))

                # 4️⃣ Tentukan tanggal fallback
                if not resolved_date:
                    if stock_picking:
                        scheduled_dt = stock_picking.scheduled_date or stock_picking.date_done
                        if scheduled_dt:
                            resolved_date = scheduled_dt.date() if hasattr(scheduled_dt, 'date') else scheduled_dt
                    if not resolved_date:
                        resolved_date = (datetime.utcnow() + timedelta(hours=7)).date()

                # 5️⃣ Tentukan prefix sesuai jenis picking
                if scrap:
                    resolved_prefix = "STJ/SP"
                    _logger.info(f"[CREATE] Detected SCRAP -> prefix {resolved_prefix}")
                elif stock_picking:
                    pick_code = stock_picking.picking_type_id.code
                    if pick_code == "incoming":
                        resolved_prefix = "STJ/TTB"
                    elif pick_code == "outgoing":
                        resolved_prefix = "STJ/DO"
                    elif pick_code == "internal":
                        resolved_prefix = "STJ/INT"
                    else:
                        resolved_prefix = "STJ"
                    _logger.info(f"[CREATE] Detected PICKING {stock_picking.name} code={pick_code} -> prefix {resolved_prefix}")
                else:
                    _logger.info("[CREATE] Inventory Valuation tanpa picking/scrap -> prefix STJ (default)")

                vals['date'] = resolved_date
                vals['name'] = self._generate_journal_sequence(resolved_date, prefix=resolved_prefix)
                _logger.info(f"[CREATE] assigned date={resolved_date} name={vals['name']} for journal 8")

            # ========== JURNAL KHUSUS ==========
            elif journal_id == 207 and not vals.get('name'):
                date_obj = fields.Date.from_string(vals.get('date', fields.Date.today()))
                vals['name'] = self._generate_journal_sequence(date_obj, prefix='JV')

            elif journal_id == 1 and not vals.get('name'):
                date_obj = fields.Date.from_string(vals.get('date', fields.Date.today()))
                vals['name'] = self._generate_journal_sequence(date_obj, prefix='SI')

            elif journal_id == 2 and not vals.get('name'):
                date_obj = fields.Date.from_string(vals.get('date', fields.Date.today()))
                vals['name'] = self._generate_journal_sequence(date_obj, prefix='PI')

            # ========== BANK / CASH ==========
            elif journal_id:
                journal = self.env['account.journal'].browse(journal_id)
                if journal.exists() and journal.type in ('bank', 'cash') and not vals.get('name'):
                    date_obj = fields.Date.from_string(vals.get('date', fields.Date.context_today(self)))
                    prefix = f"STJ/{journal.code}" if journal.code else "STJ"
                    vals['name'] = self._generate_journal_sequence(date_obj, prefix=prefix)
                    _logger.info(f"[CREATE] bank/cash journal -> prefix={prefix} name={vals['name']}")

        return super().create(vals_list)

    def write(self, vals):
        if 'invoice_date' in vals and 'date' not in vals:
            if not self.date or self.date == self.invoice_date:
                vals['date'] = vals['invoice_date']
        return super().write(vals)

    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        """ Setting Accounting Date supaya sama dengan Bill Date ketika dirubah """
        if self.invoice_date:
            self.date = self.invoice_date

    def _generate_journal_sequence(self, date_obj, prefix):
        """Membuat sequence format Prefix YY/MM/XXXXXX"""
        seq_prefix = f"{prefix} {date_obj.strftime('%y/%m')}/"
        last_entry = self.search([('name', 'like', seq_prefix)], order='name desc', limit=1)
        last_number = 1
        if last_entry and last_entry.name:
            try:
                last_number = int(last_entry.name.split('/')[-1]) + 1
            except Exception:
                pass
        return f'{seq_prefix}{str(last_number).zfill(5)}'
