from odoo import api, fields, models, Command, _

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
   # https://om-omegamas-staging-26316553.dev.odoo.com/odoo/action-31/668?debug=1

    # SECTION PIUTANG

    x_year = fields.Integer(
        compute='func_year',
    )
    def func_year(self):        
        for record in self:
            today = record.date        
            if record.date:
                if today.month == 1:
                    year = record.date.year - 1
                    record['x_year'] = year    
                else:
                    year = record.date.year
                    record['x_year'] = year
            else:
                record['x_year'] = 0

    x_akhir = fields.Integer(
        compute='func_akhir',
    )
    def func_akhir(self):
        for record in self:
            if not record.date:
                record['x_akhir'] = 0
                continue
            today = record.date
            # Tanggal pertama bulan ini (misal: 2025-12-01)
            first_day_of_current_month = datetime.date(today.year, today.month, 1)
            # 2. Tentukan bulan dan tahun sebelumnya
            if today.month == 1:
                # Jika bulan ini Januari, bulan sebelumnya adalah Desember tahun lalu
                previous_month = 12
                previous_year = today.year - 1
            else:
                # Selain itu, kurangi 1 dari bulan saat ini
                previous_month = today.month - 1
                previous_year = today.year
            # Tanggal pertama bulan sebelumnya (misal: 2025-11-01)
            first_day_of_previous_month = datetime.date(previous_year, previous_month, 1)
            # 3. Hitung selisih hari (timedelta)
            # Selisih antara tanggal pertama bulan ini dan bulan sebelumnya adalah jumlah hari di bulan sebelumnya.
            # Contoh: (2025-12-01) - (2025-11-01) = 30 hari (jumlah hari di bulan November)
            day_difference = first_day_of_current_month - first_day_of_previous_month
            # 4. Ambil jumlah hari (integer)
            jumlah_hari_bulan_sebelumnya = day_difference.days
            # 5. Tetapkan nilai
            record['x_akhir'] = jumlah_hari_bulan_sebelumnya

    x_month = fields.Integer(
        compute='func_month',
    )
    def func_month(self):
        for record in self:
            today = record.date
            if today.month:
                if today.month == 1:
                    record['x_month'] = 12
                else:
                    record['x_month'] = today.month - 1
            else:
                record['x_month'] = 0 

    # 1 SECTION PIUTANG
    x_saldo_awal_piutang = fields.Monetary(
        currency_field='fun_x_saldo_awal_piutang',
    )
   
    @api.depends('date','parent_state')
    def fun_x_saldo_awal_piutang(self):
        for rec in self:
            month_number = rec.x_month
            month_year = rec.x_year 
            month_date = rec.x_akhir 
            # 2. Contoh Penggunaan (misalnya untuk membuat string tanggal)
            if month_number:
                date_string_start = f"{month_year}-{month_number}-01"
                date_string_end = f"{month_year}-{month_number}-{month_date}"
                # SINTAKS LAMA: SALAH
                # SINTAKS BARU: BENAR
                MoveLine = self.env['account.move.line']
                domain = ["&", "&", ("date", ">=", date_string_start), ("date", "<=", date_string_end), ('parent_state', '=', 'posted'), ]
                piutang_moves = MoveLine.search(domain)
                # Odoo secara implisit akan menggabungkan semua kriteria dengan operator '&'
                # kecuali Anda secara eksplisit menambahkan operator '|'.
                # domain = ["&", ("move_id.move_type", "=", "in_invoice"), ("parent_state", "=", "posted"))]        
                x_saldo_piutang = sum(line.x_saldo_piutang for line in piutang_moves)  
                rec['x_saldo_awal_piutang'] = x_saldo_piutang
            else:
                rec['x_saldo_awal_piutang'] = 0  
    
    # 2 SECTION PIUTANG
    x_amount_total = fields.Monetary(related='move_id.amount_total', string='Faktur Penjualan')                

    # 3 SECTION PIUTANG            
    x_studio_penerimaan_penjualan = fields.Monetary(
        currency_field='fun_x_studio_penerimaan_penjualan',
    )
   
    @api.depends('date','move_id')
    def fun_x_studio_penerimaan_penjualan(self):
        for rec in self:
            if rec.move_id.payment_state in ["paid"]:
                rec['x_studio_penerimaan_penjualan'] = rec.move_id.amount_total_signed
            else:
                rec['x_studio_penerimaan_penjualan'] = 0            

    # 4 SECTION PIUTANG
    x_return_piutang = fields.Monetary(
        currency_field='fun_x_return_piutang',
    )   

    @api.depends('move_id')
    def fun_x_return_piutang(self):
        # x_return_piutang
        for rec in self:
            if rec.move_id.reversal_move_ids:        
                filtered_lines = rec.move_id.reversal_move_ids
                amount_total  = sum(line.amount_total  for line in filtered_lines)       
                rec['x_return_piutang'] = amount_total    
            else:
                rec['x_return_piutang'] = 0

    # 5 SECTION PIUTANG
    x_uang_muka_piutang = fields.Monetary(
        currency_field='fun_x_uang_muka_piutang',
    )   

    @api.depends('move_id')
    def fun_x_uang_muka_piutang(self):
        # x_uang_muka_piutang
        for rec in self:
            filtered_lines = rec.move_id.invoice_line_ids.filtered(
                lambda line: line.account_id.id == 316
            )        
            if filtered_lines:        
                price_subtotal = sum(line.price_subtotal for line in filtered_lines)  
                rec['x_uang_muka_piutang'] = price_subtotal
            else:
                rec['x_uang_muka_piutang'] = 0

    # 6 section piutang
    x_bukti_jurnal_piutang = fields.Monetary(
        currency_field='fun_x_bukti_jurnal_piutang',
    )   
    @api.depends('move_id')
    def fun_x_bukti_jurnal_piutang(self):
        # x_bukti_jurnal_piutang
        for rec in self:
            filtered_lines = rec.move_id.filtered(
                lambda line: line.journal_id.id == 207
            )        
            if filtered_lines:      
                amount_total_signed = sum(line.amount_total_signed for line in filtered_lines)               
                rec['x_bukti_jurnal_piutang'] = amount_total_signed
            else:
                rec['x_bukti_jurnal_piutang'] = 0  

     
    # 7 section piutang                    
    x_saldo_piutang = fields.Monetary(
        currency_field='fun_x_saldo_piutang',
    )   
    @api.depends('x_amount_total','x_studio_penerimaan_penjualan','x_return_piutang','x_uang_muka_piutang','x_bukti_jurnal_piutang')  
    def fun_x_saldo_piutang(self):
        # x_saldo_piutang
        for rec in self:
            x_amount_total = rec.x_amount_total
            x_studio_penerimaan_penjualan = rec.x_studio_penerimaan_penjualan
            x_return_piutang = rec.x_return_piutang
            x_uang_muka_piutang = rec.x_uang_muka_piutang
            x_bukti_jurnal_piutang =  rec.x_bukti_jurnal_piutang
            saldo = x_amount_total - x_studio_penerimaan_penjualan - x_return_piutang - x_uang_muka_piutang - x_bukti_jurnal_piutang
            if saldo:        
                rec['x_saldo_piutang'] = saldo
            else:
                rec['x_saldo_piutang'] = 0

            




    # UTANG
    # SECTION UTANG
    
    # 1 SECTION UTANG
    x_saldo_awal_utang = fields.Monetary(
        currency_field='fun_x_saldo_awal_utang',
    )
    
    @api.depends('move_id')
    def fun_x_saldo_awal_utang(self):
        # x_saldo_awal_piutang
        for rec in self:
            month_number = rec.x_month 
            month_year = rec.x_year 
            month_date = rec.x_akhir 
            # 2. Contoh Penggunaan (misalnya untuk membuat string tanggal)
            if month_number:
                date_string_start = f"{month_year}-{month_number}-01"
                date_string_end = f"{month_year}-{month_number}-{month_date}"
                domain = ["&", "&",("move_id.move_type", "=", "in_invoice"), ("date", ">=", date_string_start), ("date", "<=", date_string_end)]        
                MoveLine = self.env['account.move.line']
                piutang_moves = MoveLine.search(domain)
                x_saldo_utang = sum(line.x_saldo_utang for line in piutang_moves)
                rec['x_saldo_awal_utang'] = x_saldo_utang
            else:
                rec['x_saldo_awal_utang'] = 0
            
            
    # 2 SECTION UTANG    
    x_faktur_pembelian_utang = fields.Monetary(
        compute='fun_x_faktur_pembelian_utang',
        string='Faktur Penjualan')

    @api.depends('move_id')
    def fun_x_faktur_pembelian_utang(self):
        # x_faktur_pembelian_utang
        for rec in self:
            filtered_lines = rec.move_id.filtered(
                lambda line: line.move_type == 'in_invoice'
            )        
            if filtered_lines:        
                amount_total = sum(line.amount_total for line in filtered_lines)          
                rec['x_faktur_pembelian_utang'] = amount_total
            else:
                rec['x_faktur_pembelian_utang'] = 0
            
    # 3 SECTION UTANG                
    x_pembayaran_pemasok_utang = fields.Monetary(
        currency_field='fun_x_pembayaran_pemasok_utang',
    )   
    @api.depends('move_id')    
    def fun_x_pembayaran_pemasok_utang(self):
        # x_pembayaran_pemasok_utang
        for rec in self:
            filtered_lines = rec.move_id.filtered(
                lambda line: line.move_type == 'in_invoice'
            )        
            if filtered_lines:      
                amount_total_signed = sum(line.amount_total_signed for line in filtered_lines)  
                rec['x_pembayaran_pemasok_utang'] = amount_total_signed
            else:
                rec['x_pembayaran_pemasok_utang'] = 0
            
    # 4 SECTION UTANG    
    x_return_pembelian_utang = fields.Monetary(
        currency_field='fun_x_return_pembelian_utang',
    )   
    @api.depends('move_id')       
    def fun_x_return_pembelian_utang(self):
        # x_return_pembelian_utang
        for rec in self:
            if rec.move_id.reversal_move_ids:   
                filtered_lines = rec.move_id.reversal_move_ids
                amount_total  = sum(line.amount_total  for line in filtered_lines)       
                rec['x_return_pembelian_utang'] = amount_total         
                # rec['x_return_pembelian_utang'] = 1
            else:
                rec['x_return_pembelian_utang'] = 0             
             
    # 5 SECTION UTANG                    
    x_uang_muka_utang = fields.Monetary(
        currency_field='fun_x_uang_muka_utang',
    )   
    @api.depends('move_id')       
    def fun_x_uang_muka_utang(self):
        # x_uang_muka_utang
        for rec in self:
            filtered_lines = rec.move_id.invoice_line_ids.filtered(
                lambda line: line.account_id.id == 283
            )        
            if filtered_lines:        
                price_subtotal = sum(line.price_subtotal for line in filtered_lines)
                rec['x_uang_muka_utang'] = price_subtotal
            else:
                rec['x_uang_muka_utang'] = 0                
            
    # 6 SECTION UTANG                  
    x_bukti_jurnal_utang = fields.Monetary(
        currency_field='fun_x_bukti_jurnal_utang',
    )   
    def fun_x_bukti_jurnal_utang(self):
        # x_bukti_jurnal_utang
        for rec in self:
            filtered_lines = rec.move_id.filtered(
                lambda line: line.journal_id.id == 207
            )        
            if filtered_lines:       
                amount_total_signed = sum(line.amount_total_signed for line in filtered_lines)           
                rec['x_bukti_jurnal_utang'] = amount_total_signed
            else:
                rec['x_bukti_jurnal_utang'] = 0                
                
    # 7 SECTION UTANG                   
    x_saldo_utang = fields.Monetary(
        currency_field='fun_x_saldo_utang',
    )  
    @api.depends('x_faktur_pembelian_utang','x_pembayaran_pemasok_utang','x_return_pembelian_utang','x_uang_muka_utang','x_bukti_jurnal_utang')   
    def fun_x_saldo_utang(self):
        # x_saldo_utang
        for rec in self:
            x_faktur_pembelian_utang =  rec.x_faktur_pembelian_utang
            x_pembayaran_pemasok_utang =  rec.x_pembayaran_pemasok_utang
            x_return_pembelian_utang =  rec.x_return_pembelian_utang
            x_uang_muka_utang =  rec.x_uang_muka_utang
            x_bukti_jurnal_utang =  rec.x_bukti_jurnal_utang
            
            saldo = x_faktur_pembelian_utang - x_pembayaran_pemasok_utang - x_return_pembelian_utang - x_uang_muka_utang + x_bukti_jurnal_utang
            if saldo:        
                rec['x_saldo_utang'] = saldo
            else:
                rec['x_saldo_utang'] = 0