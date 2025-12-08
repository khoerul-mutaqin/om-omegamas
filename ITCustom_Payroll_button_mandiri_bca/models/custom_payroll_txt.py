from odoo import models, fields, api
import base64
import io
from datetime import datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    export_date = fields.Date(string="Tanggal Pembayaran", default=fields.Date.context_today)

    def open_export_bca_modal(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pilih Tanggal Pembayaran',
            'res_model': 'hr.payslip.wizard.bca',
            'view_mode': 'form',
            'target': 'new',
        }

    def export_to_bca(self, export_date=None):
        if not self:
            return

        output = io.StringIO()
        
        # Format tanggal berdasarkan input user
        today_date = export_date.strftime('%d') if export_date else datetime.today().strftime('%d')
        month_year = export_date.strftime('%m%Y') if export_date else datetime.today().strftime('%m%Y')
        
        total_net_wage = 0
        row_count = 0
        rows = []
        
        for payslip in self:
            account_number = payslip.employee_id.bank_account_id.acc_number or "No Rek"
            net_wage = payslip.net_wage or 0
            emp_id = payslip.employee_id.barcode or "0000000000"
            department = payslip.employee_id.department_id.name[:10] if payslip.employee_id.department_id else "DEPT"
            
            formatted_account_number = f"0{account_number.strip()}"
            formatted_net_wage = str(int(net_wage)).zfill(13)
            formatted_emp_id = emp_id.zfill(10)
            employee_name = payslip.employee_id.name.upper().ljust(30)[:30]
            department = department.ljust(10)[:10]
            
            formatted_line = (
                f"{formatted_account_number}{formatted_net_wage}00"
                f"{formatted_emp_id}{employee_name}{department}"
            )
            formatted_line = formatted_line.ljust(70)[:70]  # Pastikan panjang 70 karakter
            
            rows.append(formatted_line + "\n")
            total_net_wage += int(net_wage)
            row_count += 1

        row_count_formatted = str(row_count).zfill(6)
        total_net_wage_formatted = str(total_net_wage).zfill(14)

        first_line = (
            f"00000000000008900049omeg{today_date}010890500919001"
            f"{row_count_formatted}{total_net_wage_formatted}.00{month_year}"
        )
        first_line = first_line.ljust(70)[:70]  # Pastikan panjang 70 karakter
        
        output.write(first_line + "\n")
        output.writelines(rows)
        
        # Simpan file sebagai attachment di Odoo
        file_content = output.getvalue()
        output_file = base64.b64encode(file_content.encode('utf-8'))
        
        attachment = self.env['ir.attachment'].create({
            'name': f'Payslip_BCA_{today_date}{month_year}.txt',
            'type': 'binary',
            'datas': output_file,
            'res_model': 'hr.payslip',
            'res_id': self[0].id,  # Pakai salah satu payslip untuk attach file
            'mimetype': 'text/plain'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
