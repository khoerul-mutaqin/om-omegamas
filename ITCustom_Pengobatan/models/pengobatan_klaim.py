from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import base64
import io
import xlsxwriter

class PengobatanKlaim(models.Model):
    _name = 'pengobatan.klaim'
    _description = 'Pengobatan Klaim'

    name = fields.Char(string='Deskripsi Klaim', compute='_compute_name', store=True, default='Draft')
    employee_id = fields.Many2one(
        'hr.employee',
        string='Nama Karyawan',
        required=True,
        domain=lambda self: self._get_employee_domain()
    )
    nominal = fields.Float(string='Nominal')
    keterangan = fields.Text(string='Keterangan')
    tanggal_klaim = fields.Date(string='Tanggal Klaim')

    upload_file = fields.Binary(
        string="Upload File",
        required=True,
    )
    
    filename = fields.Char("Filename")

    is_image = fields.Boolean("Is Image", compute="_compute_file_type", store=True)
    is_pdf = fields.Boolean("Is PDF", compute="_compute_file_type", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    kategori = fields.Selection([
        ('rawat_jalan', 'Rawat Jalan'),
        ('kacamata', 'Kacamata'),
    ], string='Kategori', required=True)

    kacamata = fields.Selection([
        ('frame_lensa', 'Frame & Lensa'),
        ('frame', 'Frame'),
        ('lensa', 'Lensa'),
    ], string='Frame & Lensa')

    @api.model
    def create(self, vals):
        if not vals.get('tanggal_klaim'):
            raise ValidationError("Tanggal klaim harus diisi terlebih dahulu.")
        
        tanggal = fields.Date.from_string(vals['tanggal_klaim'])
        prefix = f"RMQ-{tanggal.strftime('%Y%m')}-"

        last_record = self.search([
            ('name', 'like', prefix + '%')
        ], order='name desc', limit=1)

        if last_record and last_record.name:
            last_number = int(last_record.name[-7:])
        else:
            last_number = 0

        new_number = last_number + 1
        vals['name'] = f"{prefix}{str(new_number).zfill(7)}"

        return super(PengobatanKlaim, self).create(vals)

    @api.depends('filename')
    def _compute_file_type(self):
        for record in self:
            if record.filename:
                ext = record.filename.lower().split('.')[-1]
                record.is_image = ext in ['jpg', 'jpeg', 'png', 'gif']
                record.is_pdf = ext == 'pdf'
            else:
                record.is_image = False
                record.is_pdf = False

    @api.model
    def _get_employee_domain(self):
        # Clear the cache untuk memastikan data terbaru diambil
        self.env['pengobatan.alokasi'].clear_caches()
        employee_ids = self.env['pengobatan.alokasi'].search([]).mapped('employee_id.id')
        return [('id', 'in', employee_ids)]

    def action_approve(self):
        for rec in self:
            rec.state = 'approve'

    def action_paid(self):
        for rec in self:
            rec.state = 'paid'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise UserError("You can only delete records with status 'Draft' or 'Cancelled'.")
        return super(PengobatanKlaim, self).unlink()

    @api.constrains('employee_id', 'tanggal_klaim', 'nominal')
    def _check_valid_alokasi_and_nominal(self):
        Alokasi = self.env['pengobatan.alokasi']
        for rec in self:
            if not rec.employee_id or not rec.tanggal_klaim:
                continue

            alokasis = Alokasi.search([
                ('employee_id', '=', rec.employee_id.id),
                ('berlaku_mulai', '<=', rec.tanggal_klaim),
                ('berlaku_sampai', '>=', rec.tanggal_klaim),
            ])

            if not alokasis:
                raise ValidationError("Tidak ada alokasi pengobatan yang valid untuk karyawan ini pada tanggal klaim.")

            alokasi_valid = alokasis[0]
            total_klaim = sum(self.env['pengobatan.klaim'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'paid'),
                ('tanggal_klaim', '>=', alokasi_valid.berlaku_mulai),
                ('tanggal_klaim', '<=', alokasi_valid.berlaku_sampai),
                ('id', '!=', rec.id),
            ]).mapped('nominal'))

            sisa = alokasi_valid.jatah_pengobatan - total_klaim

            if sisa < rec.nominal:
                raise ValidationError("Sisa pengobatan tidak mencukupi untuk klaim ini.")

    # ✅ Method yang dibutuhkan oleh Wizard Export
    def export_klaim_action(self, ids, date_start, date_end):
        klaims = self.browse(ids)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Hasil Klaim',
            'view_mode': 'tree',
            'res_model': 'pengobatan.klaim',
            'domain': [('id', 'in', ids)],
            'context': {
                'default_date_start': str(date_start),
                'default_date_end': str(date_end),
            }
        }
        
    @api.constrains('nominal')
    def _check_nominal(self):
        for rec in self:
            if rec.nominal == 0:
                raise ValidationError("Nominal tidak boleh 0.")
