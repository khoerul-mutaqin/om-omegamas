{
    'name': 'Hitungan Otomatis Presensi',
    'version': '1.0',
    'summary': 'Modul kustom untuk field tambahan pada presensi karyawan.',
    'description': '''
        Modul ini menambahkan field dan perhitungan terkait presensi, keterlambatan, dan pulang dini pada model hr.attendance, termasuk:
        - Penjadwalan kerja (calendar_id)
        - Hari dan kode hari (hari, day_code)
        - Jam mulai dan selesai kerja (work_from, work_to)
        - Perhitungan keterlambatan (terlambat, terlambat_display, terlambat_count)
        - Perhitungan pulang dini (pulang_dini, pulang_dini_display, pulang_dini_count)
        - Presensi harian (presensi)
        - Validasi presensi (valid)
        - Alasan keterlambatan dan pulang dini
        - Meninggalkan Pekerjaan
        - Masuk Setengah Hari Dll
        ''',
    'author': 'Taufiqur Rahman',
    'depends': ['hr_attendance'],
    'data': [
        'views/hr_attendance_views.xml',
    ],
    'installable': True,
    'application': False,
}