from odoo import models, fields, api
from datetime import datetime, timedelta

class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    def _get_next_sequence(self, date):
        """ Mengambil nomor urut terakhir untuk bulan & tahun yang sama, lalu menambah 1 """
        year = date.strftime('%y')  # Ambil 2 digit tahun
        month = date.strftime('%m')  # Ambil 2 digit bulan

        # Cari nomor terakhir untuk tahun/bulan yang sama
        last_move = self.search([
            ('name', 'like', f'STJ/PBP {year}/{month}/%')
        ], order='name desc', limit=1)

        if last_move and last_move.name:
            try:
                last_number = int(last_move.name.split('/')[-1])  # Ambil angka terakhir
            except ValueError:
                last_number = 0
        else:
            last_number = 0  # Jika tidak ada, mulai dari 0

        new_number = last_number + 1  # Tambah 1 untuk nomor unik
        return f"{new_number:03d}"  # Format jadi 3 digit

    @api.model
    def create(self, vals_list):
        """ Override create untuk set nilai 'date' dari scheduled_date di stock.picking dan set nomor jurnal """
        if isinstance(vals_list, dict):
            vals_list = [vals_list]  # Pastikan format list

        for vals in vals_list:
            stock_picking = None

            # Cek apakah ada field stock_picking_id dalam vals
            stock_picking_id = vals.get('stock_picking_id')
            if stock_picking_id:
                stock_picking = self.env['stock.picking'].browse(stock_picking_id)

            # Jika tidak ditemukan dari stock_picking_id, coba cari dari field ref atau invoice_origin
            if not stock_picking and vals.get('ref'):
                stock_picking = self.env['stock.picking'].search([('name', '=', vals['ref'].split(' - ')[0])], limit=1)

            if not stock_picking and vals.get('invoice_origin'):
                stock_picking = self.env['stock.picking'].search([('name', '=', vals['invoice_origin'])], limit=1)

            # Jika stock.picking ditemukan dan memiliki scheduled_date, gunakan tanggalnya
            if stock_picking and stock_picking.scheduled_date:
                scheduled_date = stock_picking.scheduled_date + timedelta(hours=7)  # Ubah ke UTC+7
                vals['date'] = scheduled_date.date()  # Simpan hanya tanggal
            else:
                now_utc7 = datetime.utcnow() + timedelta(hours=7)  # Waktu sekarang dalam UTC+7
                vals['date'] = now_utc7.date()  # Simpan hanya tanggal

            # # Set nilai name jika belum diisi
            # if 'name' not in vals or vals.get('name') == '/':
            #     date = vals.get('date', fields.Date.today())  # Pakai date dari scheduled_date atau hari ini
            #     formatted_number = self._get_next_sequence(date)  # Ambil nomor unik
            #     year = date.strftime('%y')
            #     month = date.strftime('%m')
            #     vals['name'] = f"STJ/PBP {year}/{month}/{formatted_number}"

        records = super().create(vals_list)
        return records
