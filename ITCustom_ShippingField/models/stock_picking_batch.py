from odoo import models, fields

class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    scheduled_date = fields.Date(string='Stuffing Date')
    tujuan = fields.Char(string="Tujuan", store=True)
    # Alamat
    buyer_id = fields.Many2one('res.partner', string='Buyer', domain=[('is_company', '=', True)])
    consignee_id = fields.Many2one('res.partner', string='Consignee', domain=[('is_company', '=', True)])
    ship_to_id = fields.Many2one('res.partner', string='Ship To', domain=[('is_company', '=', True)])
    notify_party_id = fields.Many2one('res.partner', string='Notify Party', domain=[('is_company', '=', True)])
    # Tujuan Kiri
    jenis_kontainer = fields.Char(string="Jenis Kontainer", store=True)
    kode_kontainer = fields.Char(string="Kode Kontainer", store=True)
    seal = fields.Char(string="Seal", store=True)
    booking = fields.Char(string="Booking", store=True)
    shipment_mode = fields.Selection([
        ('SEA', 'SEA SHIPMENT'),
        ('FLIGHT', 'AIRFREIGHT'),
    ], string="Shipment Mode", store=True)
    penjualan = fields.Selection([
        ('EXPORT', 'EXPORT'),
        ('LOCAL', 'LOCAL'),
    ], string="Penjualan", store=True)
    do_bc = fields.Boolean(string="DO / BC", store=True)
    kurs = fields.Float(string="Kurs", store=True)
    currencies = fields.Selection([
        ('AUD', 'AUD'),
        ('EUR', 'EUR'),
        ('IDR', 'IDR'),
        ('NZD', 'NZD'),
        ('USD', 'USD'),
    ], string="Currency", store=True)
    kurs_equals = fields.Float(string="Kurs Equals", store=True)
    kurs_saat_isi_barang = fields.Float(string="Kurs Saat Isi Barang", store=True)
    # Kanan
    remark_ext = fields.Char(string='Remark External')
    remark_int = fields.Char(string='Remark Internal')
    remark_packing_list = fields.Text(string='Remark For Packing List')
    # Kiri
    feeder = fields.Char(string="Feeder", store=True)
    etd_feeder = fields.Date(string='ETD')
    eta_feeder = fields.Date(string='ETA')
    from_feeder = fields.Char(string='From')
    to_feeder = fields.Char(string='To')
    from_lengkap = fields.Char(string='From Lengkap')
    # Kanan
    mother_vessel = fields.Char(string="Mother Vessel", store=True)
    etd_vessel = fields.Date(string='ETD')
    eta_vessel = fields.Date(string='ETA')
    from_vessel = fields.Char(string='From')
    to_vessel = fields.Char(string='To')
    to_lengkap = fields.Char(string='To Lengkap')
    # Kiri
    tanggal_kirim_si = fields.Date(string='Tanggal Kirim SI')
    cara_pengiriman = fields.Char(string='Cara Pengiriman')
    revised = fields.Integer(string='Revised SI')
    tanggal = fields.Date(string='Tanggal')
    # Kanan
    forwarder = fields.Char(string='Forwarder')
    telepon = fields.Char(string='Telepon')
    pic = fields.Char(string='PIC')
    emkl = fields.Char(string='EMKL')
    fax = fields.Char(string='Fax')
    # Kiri
    no_peb = fields.Char(string='Nomor PEB')
    tanggal_peb = fields.Date(string='Tanggal PEB')
    no_bl = fields.Char(string='No B/L')
    tanggal_bl = fields.Date(string='Tanggal B/L')
    # Kanan
    no_npe = fields.Char(string='Nomor NPE')
    tanggal_npe = fields.Date(string='Tanggal NPE')
    no_coo = fields.Char(string='Nomor COO')
    tanggal_coo = fields.Date(string='Tanggal COO')