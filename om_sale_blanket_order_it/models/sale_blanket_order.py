from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta
from io import BytesIO
import qrcode
import base64


class SaleBlanketOrder(models.Model):
    _inherit = 'sale.blanket.order'
    _description = 'Backdate Sale Blanket Order'

    date_create_blanket_order = fields.Date(
        string="Create BO",
        help="Date Create Blanket Order",
        copy=False,
        default=fields.Date.today
    )
    currency_id = fields.Many2one('res.currency', string="Currency")
    req_dp_amount = fields.Monetary(string="Request DP", currency_field='currency_id')
    ket_request_dp = fields.Char('Ket Request Dp')
    production_time = fields.Integer(string="Production Time")
    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Recipient Bank',
        domain="[('partner_id.ref_company_ids', 'parent_of', company_id)]"
    )
    due_date_update_order = fields.Date(
        string="Due Date Update",
        store=True,
        copy=False,
        tracking=True
    )
    client_order_ref = fields.Char(string="PO")
    po_cust = fields.Char(string="PO Cust")
    confirmation_date_order = fields.Date(string="Confirmation Date Order")
    due_date_order = fields.Date(string="Due Date")

    billing_partner_id = fields.Many2one('res.partner', string='Billing Partner', compute='_compute_billing_partner')

    @api.depends('partner_id')
    def _compute_billing_partner(self):
        for rec in self:
            rec.billing_partner_id = rec.partner_id.parent_id if rec.partner_id.parent_id else rec.partner_id

    @api.model
    def _get_next_sequence(self, year, month):
        """Menghasilkan nomor urut (5 digit) berdasarkan tahun & bulan"""
        last_request = self.search([
            ("name", "like", f"BO {year}/{month}/%"),
        ], order="name desc", limit=1)

        if last_request:
            try:
                last_number_str = last_request.name.split('/')[-1]
                last_number = int(last_number_str)
            except (ValueError, IndexError):
                last_number = 0
            next_number = last_number + 1
            # return f"{last_number + 1:05d}"  # Tambah 1 dengan format 5 digit
        else:
            next_number = 1
            # return "00001"  # Mulai dari 00001 jika belum ada
        
        return f"{next_number:05d}"  # selalu 5 digit


    def action_confirm(self):
        """Mengubah name menjadi BO /YYYY/MM/XXX dengan tanggal dari Create BO"""
        res = super().action_confirm()  # Memanggil fungsi bawaan

        for record in self:
            if not record.date_create_blanket_order:
                raise exceptions.ValidationError("Tanggal 'Create BO' harus diisi!")

            # Konversi date_create_blanket_order ke datetime WIB (UTC+7)
            date_bo_wib = datetime.combine(record.date_create_blanket_order, datetime.min.time()) + timedelta(hours=7)

            year = date_bo_wib.strftime("%y")  # Format YY
            month = date_bo_wib.strftime("%m")  # Format MM
            sequence = self._get_next_sequence(year, month)

            new_name = f"BO {year}/{month}/{sequence}"

            # Validasi unik sebelum mengubah name
            if self.search([("name", "=", new_name)]):
                raise exceptions.ValidationError(f"Nama {new_name} sudah digunakan, mohon coba lagi.")

            record.name = new_name  # Update field name
        return res
    
    # Total Order Qty
    total_order_qty = fields.Float(
        string="Total Order",
        compute="_compute_total_qty_order"
    )

    @api.depends('line_ids.original_uom_qty')
    def _compute_total_qty_order(self):
        for order in self:
            order.total_order_qty = sum(order.line_ids.mapped('original_uom_qty'))

    amount_total_sec_price = fields.Float(
        string="Total OM Price",
        compute='_compute_amount_total_sec_price',
        store=True
    )

    @api.depends('line_ids.total_sec_price')
    def _compute_amount_total_sec_price(self):
        for order in self:
            order.amount_total_sec_price = sum(line.total_sec_price for line in order.line_ids)

    # Action button Request DP 
    def action_wizard_dp_blanket_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request DP',
            'res_model': 'wizard.request.dp.blanket.order',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_blanket_order_id': self.id,
            }
        }
        
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
