from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta
import pytz, re


class SaleBlanketOrderWizard(models.TransientModel):
    _inherit = 'sale.blanket.order.wizard'
    _description = 'Create BackDate '

    date_create_sale_order = fields.Date(
        string="Create SO",
        help="Tanggal pembuatan Sales Order",
        copy=False,
        required=True
    )

    @api.model
    def _get_next_sequence(self, year, month):
        """Menghasilkan nomor urut (5 digit) berdasarkan tahun & bulan"""
        last_request = self.env["sale.order"].search([
            ("name", "like", f"SO {year}/{month}/%"),
        ], order="name desc", limit=1)

        if last_request:
            match = re.search(rf"SO {year}/{month}/(\d+)", last_request.name)
            if match:
                last_number = int(match.group(1))
                return f"{last_number + 1:05d}"  # Format 5 digit
            else:
                raise exceptions.ValidationError(
                    f"Format nama SO tidak sesuai: {last_request.name}"
                )
        else:
            return "00001"

    def create_sale_order(self):
        """Membuat Sales Order dari Wizard dan mengisi field 'name' di sale.order"""
        res = super().create_sale_order()  # Memanggil fungsi bawaan

        for record in self:
            if not record.date_create_sale_order:
                raise exceptions.ValidationError("Tanggal 'Create SO' harus diisi!")

            # 🔍 Ambil Blanket Order dari wizard line
            wizard_line = self.env["sale.blanket.order.wizard.line"].search([
                ("wizard_id", "=", record.id)
            ], limit=1)

            if not wizard_line or not wizard_line.order_id:
                raise exceptions.ValidationError("Blanket Order tidak ditemukan di Wizard!")

            blanket_order = wizard_line.order_id  # Ambil Blanket Order

            jakarta_tz = pytz.timezone("Asia/Jakarta")
            now_jakarta = datetime.now(jakarta_tz)

            # Gabungkan tanggal dari user + jam saat ini di WIB
            local_datetime = datetime.combine(record.date_create_sale_order, now_jakarta.time())
            localized_datetime = jakarta_tz.localize(local_datetime)
            utc_datetime = localized_datetime.astimezone(pytz.utc)
            naive_utc_datetime = utc_datetime.replace(tzinfo=None)

            # 🔥 Perbaikan: Gunakan `record.date_create_sale_order`
            date_bo_wib = datetime.combine(record.date_create_sale_order, datetime.min.time()) + timedelta(hours=7)

            year = date_bo_wib.strftime("%y")  # Format YY
            month = date_bo_wib.strftime("%m")  # Format MM
            sequence = self._get_next_sequence(year, month)

            new_name = f"SO {year}/{month}/{sequence}"

            # 🔍 Perbaikan: Cari SO berdasarkan 'origin' dari Blanket Order
            sale_order = self.env["sale.order"].search([
                ("origin", "=", blanket_order.name)  # Ambil nama Blanket Order
            ], order="id desc", limit=1)

            if sale_order:
                sale_order.write({
                    "name": new_name,  # Update nama SO
                    "date_order": naive_utc_datetime,  # Set tanggal order
                    "validity_date": record.date_create_sale_order
                })
            else:
                raise exceptions.ValidationError(f"Gagal menemukan Sales Order dengan origin {blanket_order.name}")

        return res
