from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_next_sequence(self, prefix, year, month):
        """Menghasilkan nomor urut unik (5 digit) berdasarkan tahun & bulan"""
        sequence = 1  # Mulai dari 00001
        while True:
            new_sequence = f"{sequence:05d}"  # Format 5 digit (00001, 00002, ...)
            new_name = f"{prefix} {year}/{month}/{new_sequence}"

            if not self.search([("name", "=", new_name)]):
                return new_sequence  # Return jika belum ada di database

            sequence += 1  # Jika sudah ada, coba nomor berikutnya

    def _check_stock_availability(self):
        """Method untuk mengecek ketersediaan stok"""
        for picking in self:
            if picking.picking_type_id.code == 'internal':
                insufficient_stock_moves = []
                
                for move in picking.move_ids_without_package:
                    # Skip jika move sudah cancelled atau done
                    if move.state in ('cancel', 'done'):
                        continue
                        
                    # Hitung stok tersedia
                    available_qty = self.env['stock.quant']._get_available_quantity(
                        move.product_id,
                        move.location_id,
                        strict=True
                    )
                    
                    # Jika stok tidak mencukupi
                    if move.quantity > available_qty:
                        insufficient_stock_moves.append({
                            'product': move.product_id.display_name,
                            'available': available_qty,
                            'demand': move.quantity,
                            'uom': move.product_uom.name,
                            'location': move.location_id.display_name,
                            'shortage': move.quantity - available_qty
                        })
                
                # Jika ada stok yang tidak mencukupi, tampilkan error detail
                if insufficient_stock_moves:
                    error_message = _("❌ Stok tidak mencukupi untuk pengambilan!\n\n")
                    
                    for move_info in insufficient_stock_moves:
                        error_message += _(
                            "📦 Produk: %s\n"
                            "   📍 Lokasi: %s\n"
                            "   ✅ Stok tersedia: %.2f %s\n"
                            "   📋 Quantity diminta: %.2f %s\n"
                            "   ❌ Kekurangan: %.2f %s\n\n"
                        ) % (
                            move_info['product'],
                            move_info['location'],
                            move_info['available'], move_info['uom'],
                            move_info['demand'], move_info['uom'],
                            move_info['shortage'], move_info['uom']
                        )
                    
                    error_message += _("⚠️ Silakan periksa ketersediaan stok sebelum melanjutkan.")
                    raise UserError(error_message)
    
    def button_validate(self):
        """Mengubah name berdasarkan picking_type_code saat tombol Validate ditekan"""
        for record in self:
            if not record.scheduled_date:
                raise exceptions.ValidationError("Tanggal 'Scheduled Date' harus diisi!")

            # 2. Cek ketersediaan stok SEBELUM generate sequence number
            self._check_stock_availability()

            # Gunakan timezone Odoo untuk memastikan waktu sesuai dengan lokal user
            date_scheduled_wib = fields.Datetime.context_timestamp(record, record.scheduled_date)

            year = date_scheduled_wib.strftime("%y")  # Format YY
            month = date_scheduled_wib.strftime("%m")  # Format MM

            # Tentukan prefix berdasarkan picking_type_code
            picking_prefix = record.picking_type_id.sequence_code or "STRG"

            # Dapatkan nomor urut yang unik
            sequence = self._get_next_sequence(picking_prefix, year, month)
            new_name = f"{picking_prefix} {year}/{month}/{sequence}"

            record.sudo().write({"name": new_name})  # Update name dengan sudo agar tidak ada permission issue
        
        # Jalankan validasi asli dulu
        res = super().button_validate()

        # Set date_done ulang setelah proses Odoo selesai supaya sama dengan schedule date
        for record in self:
            if record.scheduled_date:
                record.sudo().write({'date_done': record.scheduled_date})

        return res

    # Total Qty Delivery
    total_delivery_qty = fields.Float(string="Total Delivered", compute="_compute_total_delivery_qty", store=True)

    @api.depends('move_ids_without_package.quantity')
    def _compute_total_delivery_qty(self):
        for picking in self:
            picking.total_delivery_qty = sum(picking.move_ids_without_package.mapped('quantity'))

    # Total Qty Sales Order
    total_sales_order_qty = fields.Float(string="Total Delivered", compute="_compute_total_sales_order_qty", store=True)

    @api.depends('move_ids_without_package.product_uom_qty')
    def _compute_total_sales_order_qty(self):
        for picking in self:
            picking.total_sales_order_qty = sum(picking.move_ids_without_package.mapped('product_uom_qty'))

    def action_add_so_products(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Products from Sales Order',
            'res_model': 'add.so.products.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
            }

        }
    
    sale_id = fields.Many2one('sale.order', string='Sales Order', compute='_compute_sale_id', store=True)
    client_order_ref = fields.Char(related='sale_id.client_order_ref', string='Customer Reference', store=True)

    @api.depends('origin')
    def _compute_sale_id(self):
        for picking in self:
            sale = self.env['sale.order'].search([('name', '=', picking.origin)], limit=1)
            picking.sale_id = sale.id if sale else False

    # --- override name_search agar bisa search otomatis by SO name / client_order_ref
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', '|',
                  ('name', operator, name),
                  ('sale_id.name', operator, name),
                  ('client_order_ref', operator, name)]
        pickings = self.search(domain + args, limit=limit)

        return pickings.name_get()
