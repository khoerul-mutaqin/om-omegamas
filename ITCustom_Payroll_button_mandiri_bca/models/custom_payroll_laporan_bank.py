from odoo import models, fields, api
import base64
import io
from datetime import datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    def export_to_bank(self):
        if not self:
            return

        import xlwt
        from xlwt import easyxf

        # Buat workbook dan worksheet
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Bank Payment')

        # Style untuk header laporan
        report_header_style = easyxf(
            'font: bold on, height 280; align: horiz center;'
        )
        
        # Style untuk sub-header
        subheader_style = easyxf(
            'font: bold on; align: horiz left;'
        )
        
        # Style untuk header tabel dengan wrap text
        table_header_style = easyxf(
            'font: bold on; align: horiz center, wrap on;'
            'borders: left thin, right thin, top thin, bottom thin;'
        )
        
        # Style untuk data dengan border dan wrap text
        border_style = easyxf(
            'align: wrap on;'
            'borders: left thin, right thin, top thin, bottom thin;'
        )

        # Dictionary untuk mapping bank ke nomor rekening perusahaan
        bank_account_mapping = {
            'Bank Mandiri': '1440005076614',
            'Bank BCA': '0890500919',
        }

        # Kelompokkan payslip berdasarkan bank dan kumpulkan data karyawan
        bank_groups = {}
        employee_details = []
        total_net_wage = 0
        
        for payslip in self:
            bank_name = payslip.employee_id.bank_account_id.bank_id.name or "Unknown Bank"
            net_wage = payslip.net_wage or 0
            total_net_wage += net_wage
            
            # Standarisasi nama bank
            if 'mandiri' in bank_name.lower():
                standardized_bank = 'Bank Mandiri'
            elif 'bca' in bank_name.lower():
                standardized_bank = 'Bank BCA'
            else:
                standardized_bank = bank_name
            
            if standardized_bank not in bank_groups:
                bank_groups[standardized_bank] = 0
            bank_groups[standardized_bank] += net_wage
            
            # Kumpulkan data karyawan untuk rincian transfer
            employee_data = {
                'bank_name': standardized_bank,
                'company_acc_no': bank_account_mapping.get(standardized_bank, '0890500919'),
                'employee_no': payslip.employee_id.barcode or '',
                'employee_name': payslip.employee_id.name or '',
                'employee_bank': standardized_bank,
                'employee_acc_no': payslip.employee_id.bank_account_id.acc_number.replace('-', '') if payslip.employee_id.bank_account_id.acc_number else '',
                'employee_acc_name': payslip.employee_id.name or '',
                'currency': 'IDR',
                'amount': net_wage
            }
            employee_details.append(employee_data)

        # Tulis header laporan
        worksheet.write_merge(0, 0, 0, 5, "Laporan Transfer Bank", report_header_style)
        worksheet.write(1, 0, "Transfer Type: BANK", subheader_style)
        worksheet.write(2, 0, "Transfer Summary", subheader_style)

        # Set lebar kolom (dalam satuan 1/256 of character width)
        worksheet.col(0).width = 2000  # No (lebar lebih kecil)
        worksheet.col(1).width = 6000  # Bank Perusahaan (lebar lebih besar)
        worksheet.col(2).width = 5000  # Company Acc No
        worksheet.col(3).width = 5000  # Company Acc Name
        worksheet.col(4).width = 3000  # Mata Uang
        worksheet.col(5).width = 4000  # Jumlah Total

        # Set tinggi baris untuk header (baris ke-4)
        worksheet.row(3).height = 500  # Tinggi baris header

        # Mulai tabel summary dari baris ke-4 (indeks 3 di xlwt)
        row_idx = 3

        # Tulis header tabel summary dengan style
        headers = [
            "No", 
            "Bank Perusahaan", 
            "Company Acc No", 
            "Company Acc Name", 
            "Mata Uang", 
            "Jumlah Total"
        ]
        
        for col_idx, header in enumerate(headers):
            worksheet.write(row_idx, col_idx, header, table_header_style)
        
        row_idx += 1

        # Tulis data summary untuk setiap bank
        row_number = 1
        for bank_name, bank_total in bank_groups.items():
            company_acc_no = bank_account_mapping.get(bank_name, '0890500919')
            
            # Format jumlah dengan separator ribuan TANPA .00
            if bank_total == int(bank_total):
                formatted_total = "{:,.0f}".format(bank_total)
            else:
                formatted_total = "{:,.2f}".format(bank_total)
            
            data = [
                f"{row_number}.",
                bank_name,
                company_acc_no,
                "PT Omega Mas",
                "IDR",
                formatted_total
            ]
            
            # Set tinggi baris untuk menyesuaikan wrap text
            worksheet.row(row_idx).height = 800  # Tinggi baris data
            
            for col_idx, value in enumerate(data):
                worksheet.write(row_idx, col_idx, value, border_style)
            
            row_idx += 1
            row_number += 1

        # Tambahkan baris kosong sebelum rincian transfer
        row_idx += 1
        worksheet.write(row_idx, 0, "Rincian Transfer", subheader_style)
        row_idx += 1

        # Set lebar kolom untuk tabel rincian transfer
        worksheet.col(0).width = 2000   # No
        worksheet.col(1).width = 5000   # Bank Perusahaan
        worksheet.col(2).width = 5000   # Company Acc No
        worksheet.col(3).width = 5000   # Company Acc Name
        worksheet.col(4).width = 4000   # Nomor Karyawan
        worksheet.col(5).width = 6000   # Nama Karyawan
        worksheet.col(6).width = 5000   # Employee Bank
        worksheet.col(7).width = 5000   # Employee Acc No
        worksheet.col(8).width = 6000   # Employee Acc Name
        worksheet.col(9).width = 3000   # Mata Uang
        worksheet.col(10).width = 4000  # Transfer Amount

        # Header untuk tabel rincian transfer
        detail_headers = [
            "No", 
            "Bank Perusahaan", 
            "Company Acc No", 
            "Company Acc Name", 
            "Nomor Karyawan", 
            "Nama Karyawan", 
            "Employee Bank", 
            "Employee Acc No", 
            "Employee Acc Name", 
            "Mata Uang", 
            "Transfer Amount"
        ]
        
        for col_idx, header in enumerate(detail_headers):
            worksheet.write(row_idx, col_idx, header, table_header_style)
        
        row_idx += 1

        # Tulis data rincian transfer
        detail_row_number = 1
        for detail in employee_details:
            # Format jumlah dengan separator ribuan TANPA .00
            amount = detail['amount']
            if amount == int(amount):
                formatted_amount = "{:,.0f}".format(amount)
            else:
                formatted_amount = "{:,.2f}".format(amount)
            
            data = [
                f"{detail_row_number}.",
                detail['bank_name'],
                detail['company_acc_no'],
                "PT Omega Mas",
                detail['employee_no'],
                detail['employee_name'],
                detail['employee_bank'],
                detail['employee_acc_no'],
                detail['employee_acc_name'],
                detail['currency'],
                formatted_amount
            ]
            
            # Set tinggi baris untuk menyesuaikan wrap text
            worksheet.row(row_idx).height = 800  # Tinggi baris data
            
            for col_idx, value in enumerate(data):
                worksheet.write(row_idx, col_idx, value, border_style)
            
            row_idx += 1
            detail_row_number += 1

        # Simpan ke buffer
        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)

        # Simpan file sebagai attachment di Odoo
        today_date = fields.Date.context_today(self).strftime('%Y%m%d')
        output_file = base64.b64encode(output.getvalue())

        attachment = self.env['ir.attachment'].create({
            'name': f'Payslip_Bank_Summary_{today_date}.xls',
            'type': 'binary',
            'datas': output_file,
            'res_model': 'hr.payslip',
            'res_id': self[0].id,
            'mimetype': 'application/vnd.ms-excel'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }