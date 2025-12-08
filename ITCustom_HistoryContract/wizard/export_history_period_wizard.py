from odoo import models, fields, api
import io
import base64
import xlsxwriter

class ExportHistoryPeriodWizard(models.TransientModel):
    _name = 'export.history.period.wizard'
    _description = 'Export Contract History By Period'

    contract_id = fields.Many2one('hr.contract', string='Kontrak', required=True, readonly=True)
    start_date = fields.Date(string='Dari Tanggal', required=True)
    end_date = fields.Date(string='Sampai Tanggal', required=True)

    def action_export_excel(self):
        self.ensure_one()

        history_records = self.env['contract.history.employee'].search([
            ('contract_id', '=', self.contract_id.id),
            ('history_start_date', '>=', self.start_date),
            ('history_start_date', '<=', self.end_date),
        ])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Riwayat Kontrak')

        # FORMAT STYLE
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })

        sub_title_format = workbook.add_format({
            'italic': True,
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter'
        })

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })

        # JUDUL
        sheet.merge_range('A1:K1', 'Perubahan Karir', title_format)

        # SUBJUDUL TANGGAL
        date_range = f"{self.start_date.strftime('%d-%m-%Y')} sampai {self.end_date.strftime('%d-%m-%Y')}"
        sheet.merge_range('A2:K2', date_range, sub_title_format)

        # JARAK 1 BARIS (A3 baris kosong)

        # HEADER TABEL (baris ke-4, index = 3)
        headers = [
            'Nomor Karyawan', 'Nama Karyawan',
            'Nama Kontrak', 'Tipe Karyawan', 'Departemen', 'Jabatan',
            'Tanggal Mulai', 'Tanggal Selesai', 'Status', 'Keterangan'
        ]
        for col_num, header in enumerate(headers):
            sheet.write(3, col_num, header, header_format)

        # ISI DATA mulai dari baris ke-5 (index = 4)
        for row_num, record in enumerate(history_records, start=4):
            employee = record.contract_id.employee_id
            status_selection = dict(record._fields['status'].selection)
            status_display = status_selection.get(record.status, '')
            sheet.write(row_num, 0, employee.barcode or '', cell_format)
            sheet.write(row_num, 1, employee.name or '', cell_format)
            sheet.write(row_num, 2, record.history_name or '', cell_format)
            sheet.write(row_num, 3, record.history_structure_type_id.name or '', cell_format)
            sheet.write(row_num, 4, record.history_department_id.name or '', cell_format)
            sheet.write(row_num, 5, record.history_job_id.name or '', cell_format)
            sheet.write(row_num, 6, record.history_start_date.strftime('%d-%m-%Y') if record.history_start_date else '', cell_format)
            sheet.write(row_num, 7, record.history_end_date.strftime('%d-%m-%Y') if record.history_end_date else '', cell_format)
            sheet.write(row_num, 8, status_display, cell_format)
            sheet.write(row_num, 9, record.keterangan or '', cell_format)

        # SET LEBAR KOLOM
        for col in range(11):
            sheet.set_column(col, col, 20)

        workbook.close()
        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': f'Riwayat_Kontrak_Period_{self.contract_id.name}.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': 'hr.contract',
            'res_id': self.contract_id.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
