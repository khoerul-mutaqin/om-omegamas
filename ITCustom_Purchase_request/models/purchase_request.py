from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    name = fields.Char(string="Request Reference", default="Draft", copy=False)
    date_start = fields.Date(string="Creation Date", required=True, default=fields.Date.context_today)

    @api.model
    def _get_next_sequence(self, year, month):
        """Menghasilkan nomor urut (3 digit) berdasarkan tahun & bulan"""
        last_request = self.search([
            ("name", "like", f"PR {year}/{month}/%"),
        ], order="name desc", limit=1)

        if last_request:
            try:
                last_number = int(last_request.name.split("/")[-1])
            except ValueError:
                last_number = 0
            return f"{last_number + 1:05d}"
        else:
            return "00001"  # Mulai dari 00001 jika belum ada

    def button_to_approve(self):
        """Mengubah name menjadi PR /YYYY/MM/XXX dengan timezone WIB saat tombol ditekan"""
        res = super().button_to_approve()  # Memanggil fungsi bawaan

        for record in self:
            if not record.date_start:
                raise exceptions.ValidationError("Tanggal 'date_start' harus diisi!")

            # Konversi date_start ke datetime dengan timezone WIB (UTC+7)
            date_start_wib = datetime.combine(record.date_start, datetime.min.time()) + timedelta(hours=7)

            year = date_start_wib.strftime("%y")  # Ambil tahun dalam format YY
            month = date_start_wib.strftime("%m")  # Ambil bulan dalam format MM
            sequence = self._get_next_sequence(year, month)

            new_name = f"PR {year}/{month}/{sequence}"

            # Validasi unik sebelum mengubah name
            if self.search([("name", "=", new_name)]):
                raise exceptions.ValidationError(f"Nama {new_name} sudah digunakan, mohon coba lagi.")

            record.name = new_name  # Ubah name menjadi format yang diinginkan
        return res
