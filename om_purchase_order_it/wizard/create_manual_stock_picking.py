from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError
import re


class CreateManualStockPicking(models.TransientModel):
    _inherit = 'create.stock.picking.wizard'
    _description = 'Menambahkan ID Draft-XX supaya tidak sama didalam inventory operation delivery'


    def create_stock_picking(self):
        StockPicking = self.env["stock.picking"]

        for wl in self.line_ids:
            if wl.product_qty < wl.qty:
                raise UserError(_("You cannot receive more than the ordered quantity."))

        # Cek apakah picking sudah ada
        stock_picking = self.picking_id

        if not stock_picking:
            # Ambil nomor Draft terakhir
            last_order = StockPicking.search([('name', 'like', 'Draft-%')], order="name desc", limit=1)
            if last_order and last_order.name:
                match = re.search(r'Draft-(\d+)', last_order.name)
                last_number = int(match.group(1)) if match else 0
            else:
                last_number = 0  # Jika tidak ada Draft sebelumnya, mulai dari 0

            new_number = last_number + 1
            draft_name = f"Draft-{new_number:02d}"

            # Persiapkan data untuk stock picking baru
            picking_data = self._prepare_picking()
            picking_data["name"] = draft_name  # Atur nama dengan format Draft-XX
            stock_picking = StockPicking.create(picking_data)

        # Assign stock picking yang baru dibuat
        self.picking_id = stock_picking

        return super(CreateManualStockPicking, self).create_stock_picking()