from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _description = 'Menambahkan ID Draft-XX supaya tidak sama didalam wizard purchase request'
    _inherit = 'purchase.request.line.make.purchase.order'

    def make_purchase_order(self):
        purchase_order_obj = self.env["purchase.order"]

        for item in self.item_ids:
            if not item.product_qty or item.product_qty <= 0:
                raise UserError(_("Enter a positive quantity."))

            # Ambil ID purchase order jika sudah ada
            purchase_order = self.purchase_order_id

            if not purchase_order:
                # Buat nomor unik "Draft-XX"
                last_order = purchase_order_obj.search(
                    [('name', 'like', 'Draft-%')], order="name desc", limit=1
                )

                if last_order and last_order.name:
                    try:
                        last_number = int(last_order.name.split('-')[-1])  # Ambil angka terakhir
                        new_number = last_number + 1
                    except ValueError:
                        new_number = 1  # Jika format salah, mulai dari 1
                else:
                    new_number = 1  # Jika tidak ada yang cocok, mulai dari Draft-01

                draft_name = f"Draft-{new_number:02d}"

                # Buat purchase order dengan nama yang baru
                po_data = self._prepare_purchase_order(
                    item.line_id.request_id.picking_type_id,
                    item.line_id.request_id.group_id,
                    item.line_id.company_id,
                    item.line_id.origin,
                )
                po_data["name"] = draft_name  # Atur nama RFQ

                purchase_order = purchase_order_obj.create(po_data)

            # Gunakan purchase order yang baru dibuat
            self.purchase_order_id = purchase_order

        return super(PurchaseRequestLineMakePurchaseOrder, self).make_purchase_order()
