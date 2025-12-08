from odoo import fields, models, api
from odoo.exceptions import UserError
from io import BytesIO
import qrcode
import base64


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Field  #
    confirmation_date_order = fields.Date(
        string='Confirmation Date',
        compute='_compute_from_blanket_order',
        store=True,
        copy=False,
        readonly=False,
        help="Confirmation Date"
    )

    due_date_order = fields.Date(
        string="Due Date",
        compute='_compute_from_blanket_order',
        store=True,
        copy=False,
        readonly=False,
        help="Due Date"
    )

    production_time = fields.Integer(
        string="Production Time",
        compute='_compute_from_blanket_order',
        store=True,
        copy=False,
        readonly=False,
        help="Production Time"
    )

    due_date_update_order = fields.Date(
        string="Due Date Update",
        compute='_compute_from_blanket_order',
        store=True,
        copy=False,
        tracking=True
    )

    count_revisi_order = fields.Integer(
        string="Revisi Order",
        copy=False,
        tracking=True
    )

    date_revisi_order = fields.Date(
        string="Date Revisi Order",
        copy=False,
        tracking=True
    )

    is_closed = fields.Boolean('Closed PO', default=False, copy=False)
    closed_badge = fields.Char(compute='_compute_closed_badge', string='Closed Badge', store=False)
    client_order_ref = fields.Char(
        string="PO",
        store=True,
        readonly=False,
    )
    po_cust = fields.Char(
        string="PO Cust", 
        compute="_compute_po_cust", 
        store=True,
        readonly=False,
    )

    def button_close(self):
        for order in self:
            if order.delivery_status != 'full':
                raise UserError("Delivery status harus 'full' sebelum bisa ditutup.")
            if order.state != 'sale':
                raise UserError("Order harus berada dalam status 'Sale Order' untuk bisa ditutup.")
            if order.invoice_status != 'invoiced':
                raise UserError("Order harus sudah sepenuhnya difakturkan (Full Invoiced) sebelum bisa ditutup.")

            order.write({
                'is_closed': True,
                'locked': True,
            })

    def _compute_closed_badge(self):
        for order in self:
            order.closed_badge = 'CLOSED' if order.is_closed else ''

    @api.depends('origin')
    def _compute_po_cust(self):
        for order in self:
            if order.origin:
                blanket = self.env['sale.blanket.order'].search([('name', '=', order.origin)], limit=1)
                order.po_cust = blanket.po_cust if blanket else False
            else:
                order.po_cust = False

    @api.depends('origin')
    def _compute_from_blanket_order(self):
        for order in self:
            if order.origin:
                blanket = self.env['sale.blanket.order'].search([('name', '=', order.origin)], limit=1)
                order.confirmation_date_order = blanket.confirmation_date_order if blanket else False
                order.due_date_order = blanket.due_date_order if blanket else False
                order.production_time = blanket.production_time if blanket else 0
                order.due_date_update_order = blanket.due_date_update_order if blanket else False
            else:
                order.confirmation_date_order = False
                order.due_date_order = False
                order.production_time = 0
                order.due_date_update_order = False

     # Total Order Qty
    total_order_qty = fields.Float(
        string="Total Order",
        compute="_compute_total_qty_order"
    )

    @api.depends('order_line.product_uom_qty')
    def _compute_total_qty_order(self):
        for order in self:
            order.total_order_qty = sum(order.order_line.mapped('product_uom_qty'))

    # Total Delivery Qty
    total_delivery_qty = fields.Float(
        string="Total Delivery",
        compute="_compute_total_qty_delivery",
    )

    @api.depends('order_line.qty_delivered')
    def _compute_total_qty_delivery(self):
        for delivery in self:
            delivery.total_delivery_qty = sum(delivery.order_line.mapped('qty_delivered'))

    def action_confirm(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Konfirmasi Order',
            'res_model': 'sale.order.alert.action.confirm',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_production_id': self.id},
        }

    def _original_button_action_confirm(self):
        old_date = self.date_order
        result = super(SaleOrder, self).action_confirm()
        if old_date and self.date_order != old_date:
            self.date_order = old_date
        return result
    
    def print_report(self):
        return {
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': 'om_sale_it.report_pro_forma_invoice_template',
            'report_file': 'om_sale_it.report_pro_forma_invoice_template',
            'data': {'model': 'sale.order', 'ids': self.ids, 'report_type': 'qweb-pdf'}
        }
    
    def get_supplier_grouped_lines(self):
        grouped = []
        for order in self:
            supplier_map = {}
            for line in order.order_line:
                if line.type_product == 'ext':
                    supplier = line.supp_order
                    # supplier = line.supp_order[:1] if line.supp_order else self.env['res.partner']
                    # supplier_map.setdefault(supplier, []).append(line)
                    if not supplier:
                        continue
                    supplier_map.setdefault(supplier, []).append(line)
            for supplier, lines in supplier_map.items():
                total_qty = sum(l.product_uom_qty for l in lines)
                total_price = 0.0
                for line in lines:
                    # Cari harga beli dari supplierinfo
                    price_found = False
                    for info in line.product_template_id.seller_ids:
                        if info.partner_id == supplier:
                            total_price += info.price * line.product_uom_qty
                            price_found = True
                            break
                    # Jika tidak ditemukan supplierinfo, gunakan 0
                    if not price_found:
                        total_price += 0.0
                grouped.append({
                    'supplier': supplier,
                    'lines': lines,
                    'order': order,
                    'total_qty': total_qty,
                    'total_price': total_price,
                })
        return {'docs': grouped,}

    def get_qr_code(self, data):
        if data:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()
        return ''

