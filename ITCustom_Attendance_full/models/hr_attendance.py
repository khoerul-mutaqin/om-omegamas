from odoo import models, fields, api
import dateutil.tz
import datetime
from datetime import timedelta



def generate_durasi_selection():
    selections = []
    for hour in range(0, 24):
        for minute in (0, 15, 30, 45):
            total_minutes = hour * 60 + minute
            label = f"{hour:02d}:{minute:02d}"
            selections.append((str(total_minutes), label))
    return selections

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    original_calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        string='Original Working Schedule',
        readonly=True,  # Field ini hanya bisa diisi sekali dan tidak bisa diubah lagi
        store=True
    )

    calendar_id = fields.Many2one(
        comodel_name='resource.calendar',
        string='Working Schedule',
        compute='_compute_calendar_id',
        store=True
    )

    hari = fields.Char(
        string="Hari",
        compute="_compute_hari"
    )

    day_code = fields.Integer(
        string='Day Code',
        compute='_compute_day_code'
    )
    
    work_from = fields.Float(
        string='Work From Float',
        compute='_compute_work_from',
        store=True
    )

    work_from_display = fields.Char(
        string='Mulai Kerja',
        compute='_compute_work_from_display'
    )
    
    istirahat_from = fields.Float(
        string='Istirahat From Float',
        compute='_compute_istirahat_from',
        store=True
    )

    istirahat_to = fields.Float(
        string='Istirahat To Float',
        compute='_compute_istirahat_to',
        store=True
    )

    work_to = fields.Float(
        string='Work To Float',
        compute='_compute_work_to',
        store=True
    )

    work_to_display = fields.Char(
        string='Jam Selesai Kerja',
        compute='_compute_work_to_display'
    )

    pulang_dini = fields.Integer(
        string='Pulang Dini (Float)',
        compute='_compute_pulang_dini_count',
        store=True
    )

    pulang_dini_display = fields.Char(
        string='(Durasi) Pulang Dini',
        compute='_compute_pulang_dini_display'
    )

    pulang_dini_count = fields.Integer(
        string='Pulang Dini',
        compute='_compute_pulang_dini_count',
        store=True
    )
    
    alasan_pulang_dini = fields.Text(
        string="Alasan Pulang Dini",
        store=True
    )

    presensi = fields.Integer(
        string='Presensi',
        compute='_compute_absen',
        default=None,
        store=True
    )

    valid = fields.Integer(
        string='Valid In',
        compute='_compute_valid',
        store=True,
        default=1
    )
    
    valid_out = fields.Integer(
        string='Valid Out',
        compute='_compute_valid_out',
        store=True,
    )
    
    terlambat = fields.Integer(
        string='Terlambat (Integer)',
        compute='_compute_terlambat',
        store=True
    )

    terlambat_display = fields.Char(
        string='(Durasi) Terlambat',
        compute='_compute_terlambat_display'
    )

    terlambat_count = fields.Integer(
        string='Terlambat',
        compute='_compute_terlambat_count',
        store=True
    )
    
    alasan_terlambat = fields.Text(
        string="Alasan Terlambat",
        store=True
    )

    insentif = fields.Integer(
        string="Insentif", 
        compute="_compute_insentif", 
        store=True
    )

    tidak_efektif = fields.Integer(
        string="Tidak Efektif", 
        compute="_compute_tidak_efektif", 
        store=True
    )
    
    lembur = fields.Integer(
        string="Lembur", 
        compute="_compute_lembur", 
        store=True
    )

    status_insentif = fields.Selection([
        ('setuju', 'Setuju'),
        ('tolak', 'Tolak')
    ], 
    string="Status Insentif", 
    default='', 
    compute="_compute_status_insentif", 
    inverse="_inverse_status_insentif", 
    store=True
    )

    catatan_insentif = fields.Text(
        string="Catatan Insentif",
        store=True
    )

    kategori_selection = fields.Selection(
        selection=[
            ('MP', 'Meninggalkan Pekerjaan'),
            ('MSH', 'Masuk Setengah Hari'),
        ],
        string='Kategori'
    )

    durasi = fields.Selection(
        selection=generate_durasi_selection(),
        string='Durasi',
        help='Durasi waktu dalam format menit'
    )

    durasi_menit = fields.Integer(
        string='Durasi Menit', 
        compute='_compute_durasi_menit', 
        store=True
    )

    msh_count = fields.Integer(
        string='MSH', 
        compute='_compute_counts', 
        store=True
    )

    mp_count = fields.Integer(
        string='MP', 
        compute='_compute_counts', 
        store=True
    )
    
    employee_type = fields.Selection(
    related='employee_id.employee_type',
    string='Employee Type',
    )
    
    @api.depends('original_calendar_id')
    def _compute_calendar_id(self):
        """
        Compute calendar_id berdasarkan original_calendar_id.
        Jika original_calendar_id sudah ada, gunakan nilai tersebut.
        Jika belum ada, gunakan resource_calendar_id dari employee.
        """
        for record in self:
            if record.original_calendar_id:
                # Gunakan original_calendar_id jika sudah ada
                record.calendar_id = record.original_calendar_id
            else:
                # Jika belum ada, gunakan resource_calendar_id dari employee
                record.calendar_id = record.employee_id.resource_calendar_id

    @api.model
    def create(self, vals):
        """
        Saat record baru dibuat, isi original_calendar_id dengan resource_calendar_id dari employee.
        """
        if 'employee_id' in vals:
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            vals['original_calendar_id'] = employee.resource_calendar_id.id
        return super(HrAttendance, self).create(vals)

    def write(self, vals):
        """
        Pastikan original_calendar_id tidak diubah setelah record dibuat.
        """
        if 'original_calendar_id' in vals:
            del vals['original_calendar_id']  # Hapus nilai original_calendar_id dari vals
        return super(HrAttendance, self).write(vals)

    @api.depends('check_in')
    def _compute_day_code(self):
        wib_timezone = dateutil.tz.gettz('Asia/Jakarta')
        
        for record in self:
            if record.check_in:
                check_in_date = record.check_in.astimezone(wib_timezone)
                record.day_code = check_in_date.weekday()  # 0=Senin, ..., 6=Minggu
            else:
                record.day_code = 0

    @api.depends('day_code', 'calendar_id')
    def _compute_work_from(self):
        for record in self:
            if record.calendar_id:
                attendance = self.env['resource.calendar.attendance'].search([
                    ('calendar_id', '=', record.calendar_id.id),
                    ('dayofweek', '=', str(record.day_code)),
                    ('day_period', '=', 'morning')
                ], limit=1)
                record.work_from = attendance.hour_from if attendance else 0.0
            else:
                record.work_from = 0.0

    @api.depends('day_code', 'calendar_id')
    def _compute_istirahat_from(self):
        for record in self:
            if record.calendar_id:
                attendance = self.env['resource.calendar.attendance'].search([
                    ('calendar_id', '=', record.calendar_id.id),
                    ('dayofweek', '=', str(record.day_code)),
                    ('day_period', '=', 'lunch')
                ], limit=1)
                record.istirahat_from = attendance.hour_from if attendance else 0.0
            else:
                record.istirahat_from = 0.0

    @api.depends('day_code', 'calendar_id')
    def _compute_istirahat_to(self):
        for record in self:
            if record.calendar_id:
                attendance = self.env['resource.calendar.attendance'].search([
                    ('calendar_id', '=', record.calendar_id.id),
                    ('dayofweek', '=', str(record.day_code)),
                    ('day_period', '=', 'lunch')
                ], limit=1)
                record.istirahat_to = attendance.hour_to if attendance else 0.0
            else:
                record.istirahat_to = 0.0

    @api.depends('work_from')
    def _compute_work_from_display(self):
        for record in self:
            hours = int(record.work_from)
            minutes = int((record.work_from - hours) * 60)
            record.work_from_display = f"{hours:02}:{minutes:02}"

    @api.depends('day_code', 'calendar_id')
    def _compute_work_to(self):
        for record in self:
            if record.calendar_id:
                attendance = self.env['resource.calendar.attendance'].search([
                    ('calendar_id', '=', record.calendar_id.id),
                    ('dayofweek', '=', str(record.day_code)),
                    ('day_period', '=', 'afternoon')
                ], limit=1)
                record.work_to = attendance.hour_to if attendance else 0.0
            else:
                record.work_to = 0.0

    @api.depends('work_to')
    def _compute_work_to_display(self):
        for record in self:
            hours = int(record.work_to)
            minutes = int((record.work_to - hours) * 60)
            record.work_to_display = f"{hours:02}:{minutes:02}"

    @api.depends('check_in', 'employee_id')
    def _compute_valid(self):
        for record in self:
            record.valid = 1  # Default to 1
            if record.check_in:
                check_in_local = record.check_in + datetime.timedelta(hours=7)
                check_in_date = check_in_local.date()

                # Cek apakah hari tersebut adalah hari kerja (Senin - Jumat)
                is_weekday = check_in_date.weekday() < 5

                # Cek apakah tanggal tersebut adalah hari libur berdasarkan calendar_id dan tanggal
                is_holiday = any(
                    leave.date_from.date() <= check_in_date <= leave.date_to.date()
                    for leave in record.calendar_id.global_leave_ids
                ) if record.calendar_id else False

                # Jika bukan hari kerja atau hari libur, tidak valid
                if not is_weekday or is_holiday:
                    record.valid = 0
                    continue

                # Cek jika sudah ada presensi di hari yang sama
                for rec in record.employee_id.attendance_ids:
                    if rec.id != record.id and rec.check_in:
                        rec_check_in_local = rec.check_in + datetime.timedelta(hours=7)
                        if rec_check_in_local.date() == check_in_date and rec.presensi == 1:
                            record.valid = 0
                            break
                        
    # @api.depends('check_in', 'work_from', 'istirahat_from', 'istirahat_to', 'valid')
    # def _compute_terlambat(self):
    #     for record in self:
    #         # Jika valid = 0, langsung set terlambat = 0
    #         if record.valid == 0:
    #             record.terlambat = 0
    #             continue

    #         if record.check_in and record.work_from:
    #             wib_timezone = dateutil.tz.gettz('Asia/Jakarta')
    #             check_in_date = record.check_in.astimezone(wib_timezone)

    #             # Konversi jam kerja ke waktu yang benar
    #             work_from_hours = int(record.work_from)
    #             work_from_minutes = int((record.work_from - work_from_hours) * 60)
    #             work_from_time = check_in_date.replace(hour=work_from_hours, minute=work_from_minutes, second=0)

    #             istirahat_from_hours = int(record.istirahat_from)
    #             istirahat_from_minutes = int((record.istirahat_from - istirahat_from_hours) * 60)
    #             istirahat_from_time = check_in_date.replace(hour=istirahat_from_hours, minute=istirahat_from_minutes, second=0)

    #             istirahat_to_hours = int(record.istirahat_to)
    #             istirahat_to_minutes = int((record.istirahat_to - istirahat_to_hours) * 60)
    #             istirahat_to_time = check_in_date.replace(hour=istirahat_to_hours, minute=istirahat_to_minutes, second=0)

    #             if check_in_date > work_from_time:
    #                 if check_in_date < istirahat_from_time:
    #                     # Terlambat sebelum istirahat, hitung langsung
    #                     delta = check_in_date - work_from_time
    #                     record.terlambat = int(delta.total_seconds() // 60)
    #                 elif check_in_date > istirahat_to_time:
    #                     # Terlambat setelah istirahat, hitung dari work_from hingga istirahat + setelah istirahat
    #                     delta_before_lunch = istirahat_from_time - work_from_time
    #                     delta_after_lunch = check_in_date - istirahat_to_time
    #                     record.terlambat = int((delta_before_lunch.total_seconds() + delta_after_lunch.total_seconds()) // 60)
    #                 else:
    #                     # Check-in saat jam istirahat, hitung keterlambatan hanya dari jam kerja setelah istirahat
    #                     delta = check_in_date - istirahat_to_time
    #                     record.terlambat = int(delta.total_seconds() // 60)
    #             else:
    #                 record.terlambat = 0
    #         else:
    #             record.terlambat = 0


    @api.depends('check_in', 'work_from', 'istirahat_from', 'istirahat_to', 'valid')
    def _compute_terlambat(self):
        for record in self:
            # Reset nilai terlambat
            record.terlambat = 0
            
            # Jika valid = 0, skip perhitungan
            if record.valid == 0:
                continue

            if record.check_in and record.work_from:
                wib_timezone = dateutil.tz.gettz('Asia/Jakarta')
                check_in_date = record.check_in.astimezone(wib_timezone)
                
                # Konversi jam kerja
                work_from_hours = int(record.work_from)
                work_from_minutes = int((record.work_from - work_from_hours) * 60)
                work_from_time = check_in_date.replace(hour=work_from_hours, minute=work_from_minutes, second=0)
                
                # Cari semua jadwal istirahat yang valid (work_from > 0)
                valid_breaks = self.env['resource.calendar.attendance'].search([
                    ('calendar_id', '=', record.calendar_id.id),
                    ('dayofweek', '=', str(record.day_code)),
                    ('day_period', '=', 'lunch'),
                    ('hour_from', '>', 0)  # Hanya jadwal dengan hour_from > 0
                ])
                
                # Jika check-in terlambat
                if check_in_date > work_from_time:
                    # Hitung total menit terlambat awal
                    total_late_minutes = (check_in_date - work_from_time).total_seconds() / 60
                    
                    # Kurangi waktu yang termasuk dalam break valid
                    for break_schedule in valid_breaks:
                        break_start = check_in_date.replace(
                            hour=int(break_schedule.hour_from),
                            minute=int((break_schedule.hour_from - int(break_schedule.hour_from)) * 60),
                            second=0
                        )
                        break_end = check_in_date.replace(
                            hour=int(break_schedule.hour_to),
                            minute=int((break_schedule.hour_to - int(break_schedule.hour_to)) * 60),
                            second=0
                        )
                        
                        # Jika check-in setelah break selesai
                        if check_in_date >= break_end:
                            # Kurangi durasi break dari total terlambat
                            total_late_minutes -= (break_end - break_start).total_seconds() / 60
                        # Jika check-in selama break
                        elif check_in_date > break_start:
                            # Hitung hanya sampai awal break
                            total_late_minutes = (break_start - work_from_time).total_seconds() / 60
                    
                    record.terlambat = max(0, int(total_late_minutes))  # Pastikan tidak negatif


    @api.depends('terlambat')
    def _compute_terlambat_display(self):
        for record in self:
            if record.terlambat:
                hours = record.terlambat // 60
                minutes = record.terlambat % 60
                record.terlambat_display = f"{hours:02}:{minutes:02}"
            else:
                record.terlambat_display = "00:00"

    @api.depends('terlambat')
    def _compute_terlambat_count(self):
        for record in self:
            record.terlambat_count = 1 if record.terlambat > 0 else 0

    @api.depends('check_in', 'check_out')
    def _compute_absen(self):
        for record in self:
            if record.check_in and record.check_out:
                # Konversi check_in ke waktu lokal (WIB - UTC+7)
                check_in_utc = record.check_in
                check_in_local = check_in_utc + datetime.timedelta(hours=7)
                check_in_date = check_in_local.date()

                employee_id = record.employee_id.id

                # Dapatkan semua record absensi untuk tanggal yang sama
                attendance_records = []
                if record.employee_id and record.employee_id.attendance_ids:
                    for rec in record.employee_id.attendance_ids:
                        if rec.check_in:
                            rec_check_in_utc = rec.check_in
                            rec_check_in_local = rec_check_in_utc + datetime.timedelta(hours=7)
                            if rec_check_in_local.date() == check_in_date:
                                attendance_records.append(rec)

                # Cari check-in pertama pada hari itu
                first_check_in = None
                if attendance_records:
                    first_check_in = min(attendance_records, key=lambda r: r.check_in)

                # Cek apakah hari tersebut adalah hari kerja (Senin - Jumat)
                is_weekday = check_in_date.weekday() < 5

                # Cek apakah tanggal tersebut adalah hari libur berdasarkan calendar_id dan tanggal
                is_holiday = any(
                    leave.date_from.date() <= check_in_date <= leave.date_to.date()
                    for leave in record.calendar_id.global_leave_ids
                ) if record.calendar_id else False

                # Jika ini adalah check-in pertama pada hari kerja dan bukan hari libur → 1, jika tidak → 0
                if first_check_in and record.id == first_check_in.id:
                    record.presensi = 1 if is_weekday and not is_holiday else 0
                else:
                    record.presensi = 0
            else:
                record.presensi = 0

    @api.depends('check_in')
    def _compute_valid_out(self):
        for record in self:
            previous_valid_out = record.valid_out  # Simpan nilai sebelumnya
            if record.check_in:
                # Konversi check_in ke waktu lokal (WIB - UTC+7)
                check_in_utc = record.check_in
                check_in_local = check_in_utc + datetime.timedelta(hours=7)
                check_in_date = check_in_local.date()

                employee_id = record.employee_id.id

                # Cek apakah hari tersebut adalah hari kerja (Senin - Jumat)
                is_weekday = check_in_date.weekday() < 5

                # Cek apakah tanggal tersebut adalah hari libur berdasarkan Working Schedule
                is_holiday = False
                if record.employee_id and record.employee_id.contract_id and record.calendar_id:
                    for leave in record.calendar_id.global_leave_ids:
                        leave_date_from = leave.date_from.date()
                        leave_date_to = leave.date_to.date()
                        if leave_date_from <= check_in_date <= leave_date_to:
                            is_holiday = True
                            break

                # Dapatkan rentang waktu lokal (WIB) untuk tanggal yang sama
                start_datetime_local = datetime.datetime.combine(check_in_date, datetime.time.min) - datetime.timedelta(hours=7)
                end_datetime_local = datetime.datetime.combine(check_in_date, datetime.time.max) - datetime.timedelta(hours=7)

                # Dapatkan semua record absensi untuk tanggal yang sama berdasarkan WIB
                attendance_records = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee_id),
                    ('check_in', '>=', start_datetime_local),
                    ('check_in', '<=', end_datetime_local),
                    ('id', '!=', record.id)
                ])

                # Jika hari kerja dan bukan hari libur, proses valid_out
                if is_weekday and not is_holiday:
                    # Set valid_out sebelumnya menjadi 0
                    attendance_records.write({'valid_out': 0})

                    # Set valid_out saat ini menjadi 1
                    record.valid_out = 1
                else:
                    record.valid_out = 0
            else:
                record.valid_out = 0

            # Trigger manual recompute jika valid_out berubah
            if record.valid_out != previous_valid_out:
                record._compute_pulang_dini_count()


    @api.model
    def compute_old_data(self):
        records = self.search([])
        records._compute_absen()

    @api.depends('check_in')
    def _compute_hari(self):
        days = {
            0: 'Senin', 1: 'Selasa', 2: 'Rabu',
            3: 'Kamis', 4: 'Jum’at', 5: 'Sabtu', 6: 'Minggu'
        }
        for record in self:
            if record.check_in:
                check_in = record.check_in

                # Konversi Manual UTC ke WIB (Tambahkan 7 jam)
                jam_baru = check_in.hour + 7
                hari_baru = check_in.weekday()

                # Jika melebihi 24 jam, geser ke hari berikutnya
                if jam_baru >= 24:
                    jam_baru -= 24  # Sesuaikan kembali dalam 0-23 jam
                    hari_baru += 1  # Geser ke hari berikutnya

                    # Jika hari_baru melebihi 6 (Minggu), kembali ke 0 (Senin)
                    if hari_baru > 6:
                        hari_baru = 0

                # Set hasil hari dalam WIB
                record.hari = days[hari_baru]
            else:
                record.hari = ''

    @api.depends('check_in', 'check_out', 'valid_out', 'kategori_selection')
    def _compute_pulang_dini_count(self):
        for record in self:
            # If kategori_selection is 'MP', set pulang_dini and pulang_dini_count to 0
            if record.kategori_selection == 'MP':
                record.pulang_dini_count = 0
                record.pulang_dini = 0
                continue

            record.pulang_dini_count = 0  # Default value
            record.pulang_dini = 0  # Default value

            if record.valid_out != 1:
                continue

            if record.check_in and record.check_out:
                # Konversi check_in dan check_out ke waktu lokal (WIB - UTC+7)
                check_in_local = record.check_in + datetime.timedelta(hours=7)
                check_out_local = record.check_out + datetime.timedelta(hours=7)
                check_in_date = check_in_local.date()

                # Dapatkan semua record absensi untuk tanggal yang sama
                attendance_records = [
                    rec for rec in record.employee_id.attendance_ids
                    if rec.check_in and (rec.check_in + datetime.timedelta(hours=7)).date() == check_in_date
                ]

                # Ambil work_to langsung dari field
                work_to = record.work_to or 0

                # Konversi work_to ke waktu datetime dengan aman
                hours = int(work_to)
                minutes = int(round((work_to - hours) * 60))
                work_to_time = datetime.time(hours, minutes)
                work_to_datetime = datetime.datetime.combine(check_in_date, work_to_time)

                # Cek apakah hari tersebut adalah hari kerja (Senin - Jumat)
                is_weekday = check_in_date.weekday() < 5

                # Cek apakah tanggal tersebut adalah hari libur berdasarkan Working Schedule
                is_holiday = False
                if record.calendar_id and record.calendar_id.global_leave_ids:
                    for leave in record.calendar_id.global_leave_ids:
                        if leave.date_from.date() <= check_in_date <= leave.date_to.date():
                            is_holiday = True
                            break

                # Hitung hanya untuk check-out terakhir di hari tersebut dan jika hari kerja & bukan libur
                max_record_id = max([rec.id for rec in attendance_records]) if attendance_records else None
                if record.id == max_record_id:
                    if is_weekday and not is_holiday:
                        if check_out_local < work_to_datetime:
                            record.pulang_dini_count = 1
                            delta = work_to_datetime - check_out_local
                            record.pulang_dini = int(delta.total_seconds() // 60)
                        else:
                            record.pulang_dini_count = 0
                            record.pulang_dini = 0
                    else:
                        record.pulang_dini_count = 0
                        record.pulang_dini = 0

    @api.depends('pulang_dini')
    def _compute_pulang_dini_display(self):
        for record in self:
            if record.pulang_dini:
                hours = record.pulang_dini // 60
                minutes = record.pulang_dini % 60
                record.pulang_dini_display = f"{hours:02}:{minutes:02}"
            else:
                record.pulang_dini_display = "00:00"
            
    @api.depends('worked_hours')
    def _compute_insentif(self):
        for record in self:
            # Gunakan zona waktu Indonesia WIB (UTC+7)
            wib_offset = 7
            check_in_date = (record.check_in + timedelta(hours=wib_offset)).date() if record.check_in else None

            # Cek apakah hari tersebut adalah hari libur (Sabtu atau Minggu)
            is_weekend = check_in_date and check_in_date.weekday() in [5, 6]

            # Cek apakah tanggal tersebut adalah hari libur berdasarkan tanggal saja
            is_holiday = any(
                leave.date_from.date() <= check_in_date <= leave.date_to.date()
                for leave in record.calendar_id.global_leave_ids
            ) if record.calendar_id and check_in_date else False

            # Jika worked_hours >= 4 dan hari tersebut libur atau akhir pekan → insentif = 1
            if record.worked_hours >= 4 and (is_weekend or is_holiday):
                record.insentif = 1
            else:
                record.insentif = 0

    @api.depends('check_in', 'check_out')
    def _compute_tidak_efektif(self):
        for record in self:
            if record.check_in and record.check_out:
                # Konversi check_in ke waktu lokal (WIB - UTC+7)
                check_in_utc = record.check_in
                check_in_local = check_in_utc + datetime.timedelta(hours=7)
                check_in_date = check_in_local.date()

                # Dapatkan semua record absensi untuk tanggal yang sama
                attendance_records = []
                if record.employee_id and record.employee_id.attendance_ids:
                    for rec in record.employee_id.attendance_ids:
                        if rec.check_in:
                            rec_check_in_utc = rec.check_in
                            rec_check_in_local = rec_check_in_utc + datetime.timedelta(hours=7)
                            if rec_check_in_local.date() == check_in_date:
                                attendance_records.append(rec)

                # Cari check-in pertama pada hari itu
                first_check_in = None
                if attendance_records:
                    first_check_in = min(attendance_records, key=lambda r: r.check_in)

                # Cek apakah tanggal tersebut adalah hari libur berdasarkan calendar_id dan tanggal
                is_holiday = any(
                    leave.date_from.date() <= check_in_date <= leave.date_to.date() and leave.work_entry_type_id.code == 'PANL'
                    # leave.work_entry_type_id.code in ['PANL', 'IDLEAVE140']
                    for leave in record.calendar_id.global_leave_ids
                ) if record.calendar_id else False

                # Jika ini adalah check-in pertama pada hari kerja dan bukan hari libur → 1, jika tidak → 0
                if first_check_in and record.id == first_check_in.id:
                    record.tidak_efektif = 1 if is_holiday else 0
                else:
                    record.tidak_efektif = 0
            else:
                record.tidak_efektif = 0

    @api.depends('worked_hours')
    def _compute_lembur(self):
        for record in self:
            # Gunakan zona waktu Indonesia WIB (UTC+7)
            wib_offset = 7
            check_in_date = (record.check_in + timedelta(hours=wib_offset)).date() if record.check_in else None

            # Cek apakah hari tersebut adalah hari libur (Sabtu atau Minggu)
            is_weekend = check_in_date and check_in_date.weekday() in [5, 6]

            # Cek apakah tanggal tersebut adalah hari libur berdasarkan tanggal saja
            is_holiday = any(
                leave.date_from.date() <= check_in_date <= leave.date_to.date()
                for leave in record.calendar_id.global_leave_ids
            ) if record.calendar_id and check_in_date else False

            # Jika worked_hours >= 4 dan hari tersebut libur atau akhir pekan → lembur = 1
            if record.worked_hours >= 4 and (is_weekend or is_holiday):
                record.lembur = 1
            else:
                record.lembur = 0
                

    @api.depends('insentif')
    def _compute_status_insentif(self):
        for record in self:
            if record.insentif == 1:
                record.status_insentif = 'setuju'
            else:
                record.status_insentif = ''

    def _inverse_status_insentif(self):
        for record in self:
            if record.status_insentif != 'setuju':
                record.insentif = 0
            elif record.status_insentif == 'setuju':
                record.insentif = 1

    @api.depends('durasi')
    def _compute_durasi_menit(self):
        for record in self:
            record.durasi_menit = int(record.durasi) if record.durasi else 0

    @api.depends('kategori_selection')
    def _compute_counts(self):
        for record in self:
            record.msh_count = 1 if record.kategori_selection == 'MSH' else 0
            record.mp_count = 1 if record.kategori_selection == 'MP' else 0