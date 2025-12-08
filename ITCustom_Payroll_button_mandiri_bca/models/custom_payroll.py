from odoo import models, fields, api
import base64
import csv
import io
from datetime import datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    export_date = fields.Date(string="Tanggal Pembayaran", default=fields.Date.context_today)

    def open_export_mandiri_modal(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pilih Tanggal Pembayaran',
            'res_model': 'hr.payslip.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def export_to_mandiri(self, export_date=None):
        if not self:
            return

        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Format tanggal berdasarkan input user
        today_date = export_date.strftime('%Y%m%d') if export_date else datetime.today().strftime('%Y%m%d')

        total_net_wage = 0
        row_count = 0
        rows = []

        # Dictionary nama bulan dalam Bahasa Indonesia
        bulan_dict = {
            '01': 'Januari', '02': 'Februari', '03': 'Maret', '04': 'April',
            '05': 'Mei', '06': 'Juni', '07': 'Juli', '08': 'Agustus',
            '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Desember'
        }

        for payslip in self:
            bank_name = payslip.employee_id.bank_account_id.bank_id.name or "Unknown Bank"
            net_wage = payslip.net_wage or 0
            account_number = payslip.employee_id.bank_account_id.acc_number or "No Rek"
            total_net_wage += net_wage
            row_count += 1
            formatted_account_number = account_number.replace("-", "") if account_number else ""

            # Ambil bulan & tahun dari start date period slip gaji
            if payslip.date_from:
                bulan = payslip.date_from.strftime('%m')  # Ambil nomor bulan (01, 02, dst.)
                tahun = payslip.date_from.strftime('%Y')  # Ambil tahun
                bulan_text = bulan_dict.get(bulan, 'Tidak Valid')
                bulan_tahun = f"{bulan_text} {tahun}"
            else:
                bulan_tahun = datetime.today().strftime('%B %Y')  # Jika tidak ada, pakai hari ini

            # Menentukan batch_name
            if payslip.payslip_run_id:  # Jika payslip_run_id ada, gunakan nama dari hr.payslip.run
                batch_name = payslip.payslip_run_id.name
            else:  # Jika tidak ada payslip_run_id, gunakan format "Gaji Bulan Tahun"
                batch_name = f'Gaji {bulan_tahun}'

            rows.append([
                formatted_account_number,
                payslip.employee_id.name,
                "DEFAULT",
                "",
                "",
                "IDR",
                net_wage,
                batch_name,
                "",
                "IBU",
                "",
                f"Bank {bank_name}",
                "",
                "",
                "",
                "",
                "N",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "OUR",
                1,
                "E"
            ])

        # Tulis header ke CSV
        writer.writerow(["P", today_date, "1440005076614", row_count, f"{total_net_wage:.2f}"])

        # Tulis semua data payslip yang telah dikumpulkan
        for row in rows:
            writer.writerow(row)

        # Simpan file sebagai attachment di Odoo
        file_content = output.getvalue()
        output_file = base64.b64encode(file_content.encode('utf-8'))

        attachment = self.env['ir.attachment'].create({
            'name': f'Payslip_Mandiri_{today_date}.csv',
            'type': 'binary',
            'datas': output_file,
            'res_model': 'hr.payslip',
            'res_id': self[0].id,  # Pakai salah satu payslip untuk attach file
            'mimetype': 'text/csv'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
