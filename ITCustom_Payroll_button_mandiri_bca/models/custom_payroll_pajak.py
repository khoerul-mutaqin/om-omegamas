from odoo import models, fields, api
import base64
import io
from datetime import datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    def export_pajak(self):
        if not self:
            return

        import xlwt
        from xlwt import easyxf

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Pajak')

        header_style = easyxf(
            'font: bold on; align: horiz center; borders: left thin, right thin, top thin, bottom thin;'
        )
        data_style = easyxf(
            'align: horiz left; borders: left thin, right thin, top thin, bottom thin;'
        )

        headers = [
            "No", "NPWP", "NIK", "KTP", "Nama", "Alamat", 
            "Kode Objek Pajak", "Status Pajak", "Bruto"
        ]
        
        for col_idx, header in enumerate(headers):
            worksheet.write(0, col_idx, header, header_style)
            worksheet.col(col_idx).width = 5000

        row_idx = 1
        nomor = 1
        for payslip in self:
            employee = payslip.employee_id
            contract = payslip.contract_id

            # Kode Objek Pajak
            if contract.contract_type_id.name.lower() == 'kontrak':
                kode_objek_pajak = '21-100-03'
            else:
                kode_objek_pajak = '21-100-01'

            # Status Pajak
            status_pajak = dict(employee._fields['l10n_id_kode_ptkp'].selection).get(
                employee.l10n_id_kode_ptkp, "Tidak Ada"
            )

            # Bruto dari gross_wage
            bruto = (
                (payslip.gross_wage or 0.0)
                - (payslip.t_jht_comp or 0.0)
                - (payslip.t_jp_company or 0.0)
                - (payslip.p_terlambat or 0.0)
                - (payslip.p_pd or 0.0)
                - (payslip.p_mp or 0.0)
            )
            formatted_bruto = "{:,.0f}".format(bruto)

            data = [
                nomor,
                employee.npwp or '',
                employee.barcode or '',
                employee.identification_id or '',
                employee.name or '',
                employee.private_street or '',
                kode_objek_pajak,
                status_pajak,
                formatted_bruto
            ]

            for col_idx, value in enumerate(data):
                worksheet.write(row_idx, col_idx, value, data_style)
            
            row_idx += 1
            nomor += 1

        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)

        today_date = fields.Date.context_today(self).strftime('%Y%m%d')
        output_file = base64.b64encode(output.getvalue())

        attachment = self.env['ir.attachment'].create({
            'name': f'Payslip_Pajak_{today_date}.xls',
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
