# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_deposit = fields.Boolean('Is Deposit')

class AccountMove(models.Model):
    _inherit = "account.move"

    is_deposit = fields.Boolean('Is Deposit', default=False, copy=False)

    def button_cancel(self):
        for rec in self:
            purchases = self.env['purchase.order'].search([('invoice_ids', 'in', [rec.id])])
            for purchase in purchases:
                if purchase.dp_order > 0:
                    # rec.invoice_line_ids.mapped('purchase_line_id.order_id.id') == purchase.id
                    
                    dp_product = rec.invoice_line_ids.filtered(lambda x: x.is_downpayment and x.purchase_line_id.order_id.id == purchase.id)
                    purchase.dp_order -= dp_product.price_unit
                # CANCEL PO DP BLANKET WHEN CANCEL OR DELETE BILL
                if rec.is_deposit:
                    depo_product = rec.invoice_line_ids.filtered(lambda x: x.is_deposit and x.purchase_line_id.order_id.id == purchase.id)
                    purchase.dp_blanket -= depo_product.price_unit
            # CANCEL OR SET 0 PRICE UNIT ON PO LINE
            for line in rec.line_ids:
                if not line.purchase_line_id.is_deposit:
                    continue
                line.purchase_line_id.taxes_id = False
                line.purchase_line_id.price_unit = 0


        return super().button_cancel()

    def action_post(self):
        res = super().action_post()
        for line in self.line_ids:
            if not line.purchase_line_id.is_deposit:
                continue
            # Supaya tidak menambahkan price pada line purchase
            # line.purchase_line_id.taxes_id = line.tax_ids
            # line.purchase_line_id.price_unit = line.price_unit
        
        for rec in self:
            purchases = self.env['purchase.order'].search([('invoice_ids', 'in', [rec.id])])
            if purchases:
                for purchase in purchases:
                    if purchase and not rec.is_deposit:
                        dp_product = rec.invoice_line_ids.filtered(lambda x: x.is_downpayment and x.purchase_line_id.order_id.id == purchase.id)
                        purchase.dp_order += dp_product.price_unit
                    
                    if purchase and rec.is_deposit:
                        depo_product = rec.invoice_line_ids.filtered(lambda x: x.is_deposit and x.purchase_line_id.order_id.id == purchase.id)
                        purchase.dp_blanket += depo_product.price_unit
        return res

    def unlink(self):
        for rec in self:
            for line in rec.line_ids.filtered(lambda x: x.purchase_line_id != False):
                po = line.purchase_line_id.order_id
                if po and rec.invoice_line_ids:
                    for l in po.order_line:
                        if l.is_deposit and l.move_id.id == rec.id:
                            l.unlink()
        return super().unlink()
