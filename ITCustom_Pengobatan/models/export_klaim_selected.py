import io
import xlsxwriter
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64

class PengobatanKlaim(models.Model):
    _inherit = 'pengobatan.klaim'

    def action_export_selected_klaim(self):
        """Export selected klaim records directly"""
        if not self:
            raise UserError('Tidak ada klaim yang dipilih untuk diexport.')

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Data Klaim Terpilih')

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

        currency_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0.00',
            'font_size': 11
        })

        # Tulis judul
        worksheet.merge_range('A1:H1', 'Data Klaim Terpilih', header_format)

        # Header kolom
        headers = [
            {'label': 'No', 'width': 5},
            {'label': 'Nomor Klaim', 'width': 20},
            {'label': 'Nomor Karyawan', 'width': 30},
            {'label': 'Nama Karyawan', 'width': 30},
            {'label': 'Tanggal Klaim', 'width': 15},
            {'label': 'Kategori', 'width': 20},
            {'label': 'Nominal', 'width': 15},
            {'label': 'Keterangan', 'width': 40}
        ]

        for col, header in enumerate(headers):
            worksheet.write(1, col, header['label'], header_format)
            worksheet.set_column(col, col, header['width'])

        # Tulis data
        for row, klaim in enumerate(self, start=2):
            worksheet.write(row, 0, row - 1, data_format)
            worksheet.write(row, 1, klaim.name or '', data_format)
            worksheet.write(row, 2, klaim.employee_id.barcode or '', data_format)
            worksheet.write(row, 3, klaim.employee_id.name or '', data_format)
            worksheet.write(row, 4, klaim.tanggal_klaim, date_format)

            if klaim.kategori == 'rawat_jalan':
                kategori_str = 'Rawat Jalan'
            elif klaim.kategori == 'kacamata':
                if klaim.kacamata == 'frame_lensa':
                    kategori_str = 'Frame & Lensa'
                elif klaim.kacamata == 'frame':
                    kategori_str = 'Frame'
                elif klaim.kacamata == 'lensa':
                    kategori_str = 'Lensa'
                else:
                    kategori_str = 'Kacamata'
            else:
                kategori_str = ''
            worksheet.write(row, 5, kategori_str, data_format)
            worksheet.write(row, 6, klaim.nominal or 0, currency_format)
            worksheet.write(row, 7, klaim.keterangan or '', wrap_format)

        # Total nominal
        total_row = len(self) + 2
        worksheet.write(total_row, 5, 'TOTAL:', header_format)
        worksheet.write_formula(total_row, 6, f'=SUM(G3:G{total_row})', currency_format)

        worksheet.freeze_panes(2, 0)
        workbook.close()
        output.seek(0)

        filename = f"Export_Klaim_Terpilih_{fields.Date.today().strftime('%Y%m%d')}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': base64.b64encode(output.getvalue()),
            'res_model': 'pengobatan.klaim',
            'type': 'binary',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
