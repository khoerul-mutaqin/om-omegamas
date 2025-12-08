from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Add Wizard discount'

    def action_open_discount_wizard(self):
        self.ensure_one()
        return {
            'name': _("Discount"),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.discount',
            'view_mode': 'form',
            'view_id': self.env.ref('om_purchase_order_it.view_purchase_order_discount_wizard_form').id,
            'target': 'new',
        }

    def button_confirm_manual(self):
        for order in self:
            if order.state == 'draft':
                order._update_po_number()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Konfirmasi Order',
            'res_model': 'alert.confirm.purchase.order',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_purchase_id': self.id},
        }
    def _original_button_action_confirm(self):
        return super(PurchaseOrder, self).button_confirm_manual()

    def _update_po_number(self):
        """ Generate PO number based on Year/Month with WIB timezone (UTC+7) """
        for order in self:
            if order.state == 'draft':
                # Selalu gunakan datetime sekarang untuk year/month sequence
                date_now = fields.Datetime.now()

                # Convert date_now to WIB timezone
                date_wib = fields.Datetime.context_timestamp(order, date_now)

                year = date_wib.strftime('%y')
                month = date_wib.strftime('%m')

                # Find last PO in the same month & year in WIB timezone
                last_po = self.search([
                    ('name', 'like', f'PO {year}/{month}/%'),
                    ('id', '!=', order.id)  # Avoid conflict with own PO
                ], order='name desc', limit=1)

                if last_po:
                    last_number = int(last_po.name.split('/')[-1]) + 1
                else:
                    last_number = 1  # Reset to 1 if new month

                new_name = f"PO {year}/{month}/{last_number:05d}"
                order.name = new_name  # Set new name


    @api.constrains('name')
    def _check_unique_name(self):
        for order in self:
            if self.search_count([('name', '=', order.name)]) > 1:
                raise ValidationError(f"Nomor PO '{order.name}' sudah ada! Harap gunakan nomor yang unik.")
