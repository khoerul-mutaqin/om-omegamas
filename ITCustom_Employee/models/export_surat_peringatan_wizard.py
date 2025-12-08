# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_Employee/models/export_surat_peringatan_wizard.py
import io
import base64
import xlsxwriter
from odoo import models, fields, api
from odoo.exceptions import UserError

class ExportSuratPeringatanWizard(models.TransientModel):
    _name = 'export.employee.surat.peringatan.wizard'
    _description = 'Wizard Export Surat Peringatan'

    date_start = fields.Date(string='Tanggal Mulai', required=True)
    date_end = fields.Date(string='Tanggal Selesai', required=True)

    def action_export(self):
        if self.date_start > self.date_end:
            raise UserError('Tanggal Mulai tidak boleh lebih besar dari Tanggal Selesai.')

        records = self.env['employee.surat.peringatan'].search([
            ('date_reference', '>=', self.date_start),
            ('date_reference', '<=', self.date_end),
        ])

        if not records:
            raise UserError('Tidak ada data Surat Peringatan pada periode tersebut.')

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Surat Peringatan')

        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'font_size': 12
        })

        wrap_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top',
            'font_size': 11,
            'text_wrap': True
        })

        data_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'font_size': 11
        })

        date_format = workbook.add_format({
            'border': 1,
            'num_format': 'dd/mm/yyyy',
            'font_size': 11
        })

        # Tulis periode
        periode_str = f"Periode: {self.date_start.strftime('%d/%m/%Y')} - {self.date_end.strftime('%d/%m/%Y')}"
        worksheet.merge_range('A1:J1', periode_str, header_format)

        # Header kolom
        headers = [
            {'label': 'No', 'width': 5},
            {'label': 'Nomor Karyawan', 'width': 20},
            {'label': 'Nama Karyawan', 'width': 30},
            {'label': 'Departemen', 'width': 20},
            {'label': 'Posisi', 'width': 20},
            {'label': 'Tanggal Referensi', 'width': 15},
            {'label': 'Tanggal Mulai', 'width': 15},
            {'label': 'Tanggal Selesai', 'width': 15},
            {'label': 'Status', 'width': 25},
            {'label': 'Keterangan', 'width': 40}
        ]

        for col, header in enumerate(headers):
            worksheet.write(1, col, header['label'], header_format)
            worksheet.set_column(col, col, header['width'])

        # Isi data
        for row, rec in enumerate(records, start=2):
            worksheet.write(row, 0, row - 1, data_format)
            worksheet.write(row, 1, rec.employee_id.barcode or '', data_format)
            worksheet.write(row, 2, rec.employee_id.name or '', data_format)
            worksheet.write(row, 3, rec.employee_id.department_id.name if rec.employee_id.department_id else '', data_format)
            worksheet.write(row, 4, rec.employee_id.job_id.name if rec.employee_id.job_id else '', data_format)
            worksheet.write(row, 5, rec.date_reference, date_format)
            worksheet.write(row, 6, rec.start_date, date_format)
            worksheet.write(row, 7, rec.end_date, date_format)
            worksheet.write(row, 8, dict(rec._fields['status'].selection).get(rec.status, ''), data_format)
            worksheet.write(row, 9, rec.keterangan or '', wrap_format)

        worksheet.freeze_panes(2, 0)
        workbook.close()
        output.seek(0)

        filename = f"Export_Surat_Peringatan_{fields.Date.today().strftime('%Y%m%d')}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': base64.b64encode(output.getvalue()),
            'res_model': 'export.employee.surat.peringatan.wizard',
            'type': 'binary',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
