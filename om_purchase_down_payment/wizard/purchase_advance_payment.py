# Copyright 2019 Elico Corp, Dominique K. <dominique.k@elico-corp.com.sg>
# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from datetime import datetime

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.fields import Command
from odoo.tools import format_date, frozendict

class PurchaseAdvancePaymentInv(models.TransientModel):
    _name = "purchase.advance.payment.inv"
    _description = "Purchase Advance Payment Invoice"

    purchase_order_ids = fields.Many2many(
        'purchase.order', default=lambda self: self.env.context.get('active_ids'))
    advance_payment_method = fields.Selection(
        [
            ("percentage", "Deposit payment (percentage)"),
            ("fixed", "Deposit payment (fixed amount)"),
        ],
        string="What do you want to invoice?",
        default="fixed",
        required=True,
    )
    purchase_deposit_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Deposit Payment Product",
        domain=[("type", "=", "service")],
        default=lambda self: self.env.company.purchase_deposit_product_id,
    )
    amount = fields.Float(
        string="Deposit Payment Amount",
        required=True,
        help="The amount to be invoiced in advance, taxes excluded.",
    )
    deposit_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Expense Account",
        compute="_compute_deposit_account_id",
        store=True,
        readonly=False,
        domain=[("deprecated", "=", False)],
        help="Account used for deposits",
    )
    deposit_taxes_id = fields.Many2many(
        comodel_name="account.tax",
        string="Vendor Taxes",
        compute="_compute_deposit_account_id",
        store=True,
        readonly=False,
        help="Taxes used for deposits",
    )
    advance_line = fields.One2many('purchase.advance.payment.inv.line', 'advance_payment_id')
    count = fields.Integer('Count', compute='_compute_count', store=True)

    @api.depends('purchase_order_ids')
    def _compute_count(self):
        for record in self:
            record.count = len(record.purchase_order_ids)

    @api.depends("purchase_deposit_product_id")
    def _compute_deposit_account_id(self):
        product = self.purchase_deposit_product_id
        self.deposit_account_id = product.property_account_expense_id
        self.deposit_taxes_id = product.supplier_taxes_id

    # def _prepare_deposit_val_batch(self, orders, po_lines):
    #     account_id = False
    #     product = self.purchase_deposit_product_id
    #     if product.id:
    #         account_id = (
    #                 product.property_account_expense_id.id
    #                 or product.categ_id.property_account_expense_categ_id.id
    #         )
    #     if not account_id:
    #         raise UserError(
    #             _(
    #                 "There is no purchase account defined for this product: %s."
    #                 "\nYou may have to install a chart of account from "
    #                 "Accounting app, settings menu."
    #             )
    #             % (product.name,)
    #         )

    #     # if self.amount <= 0:
    #     #     raise UserError(_("The value of the deposit must be positive."))
    #     zero_dp_orders = self.advance_line.filtered(lambda x: x.dp_order == 0) 
    #     if zero_dp_orders:
    #         raise UserError(f'''The value of the order down payment {zero_dp_orders.mapped('purchase_id.name')} amount must be positive.''')

    #     for ad_line in self.advance_line:
    #         if ad_line.dp_order == 0:
    #             # raise UserError(_("The value of the deposit must be positive."))
    #             raise UserError(f'''The value of the order down payment {ad_line.purchase_id.name} amount must be positive.''')

    #     context = {"lang": orders.mapped('partner_id.lang')[0]}

    #     name = _("Deposit Payment")
    #     del context
    #     taxes = product.supplier_taxes_id.filtered(
    #         lambda r: not orders.mapped('company_id') or r.company_id.id == orders.mapped('company_id.id')[0]
    #     )
    #     if orders.mapped('fiscal_position_id') and taxes:
    #         tax_ids = orders.mapped('fiscal_position_id').map_tax(taxes).ids
    #     else:
    #         tax_ids = taxes.ids

    #     invoice_line_ids = []
    #     product_line_ids = [
    #             (
    #                 0,
    #                 0,
    #                 {
    #                     "name": order.name,
    #                     "account_id": order.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=order.order_id.fiscal_position_id).get('expense').id,
    #                     # "price_unit": amount,
    #                     "price_unit": order.price_unit,
    #                     # "quantity": order.product_qty,
    #                     "quantity": order.qty_received,
    #                     "product_uom_id": order.product_uom.id,
    #                     "product_id": order.product_id.id,
    #                     "purchase_line_id": order.id,
    #                     # "purchase_line_id": po_line.id,
    #                     "tax_ids": [(6, 0, order.taxes_id.ids)],
    #                     # "is_downpayment": False
    #                     # "analytic_distribution": po_line.analytic_distribution,
    #                 },
    #             )
    #             for order in orders.order_line.filtered(lambda x: not x.is_deposit)

    #     ]
    #     deposit_line_ids = [
    #             (
    #                 0,
    #                 0,
    #                 {
    #                     "name": order.name,
    #                     "account_id": account_id,
    #                     # "price_unit": amount,
    #                     # "price_unit": self.advance_line.filtered(lambda x: x.purchase_id.id == order.id).dp_order,
    #                     "price_unit": self.advance_line.filtered(lambda x: x.purchase_id.id == order.id).dp_order if self.advance_payment_method == 'fixed' else self.advance_line.filtered(lambda x: x.purchase_id.id == order.id).dp_order / 100 * self.advance_line.filtered(lambda x: x.purchase_id.id == order.id).dp_blanket,
    #                     "quantity": -1.0,
    #                     "product_uom_id": product.uom_id.id,
    #                     "product_id": product.id,
    #                     "purchase_line_id": po_lines.filtered(lambda x: x.order_id.id == order.id).id,
    #                     # "purchase_line_id": po_line.id,
    #                     "tax_ids": [(6, 0, tax_ids)],
    #                     "is_downpayment": True
    #                     # "analytic_distribution": po_line.analytic_distribution,
    #                 },
    #             )
    #             for order in orders
    #     ]
    #     invoice_line_ids = deposit_line_ids + product_line_ids
    #     deposit_val = {
    #         "invoice_origin": ', '.join(orders.mapped('name')),
    #         "move_type": "in_invoice",
    #         "partner_id": orders.mapped('partner_id').id,
    #         "invoice_line_ids": invoice_line_ids,
    #         "currency_id": orders.mapped('currency_id').id,
    #         # "invoice_payment_term_id": orders.payment_term_id.id,
    #         "fiscal_position_id": orders.mapped('fiscal_position_id').id
    #                               or orders.mapped('partner_id').property_account_position_id.id,
    #         # "purchase_id": order.id,
    #         # "narration": order.notes,
    #     }
        
    #     return deposit_val

    def _prepare_deposit_val_batch(self, orders, po_lines):
        account_id = False
        product = self.purchase_deposit_product_id
        if product.id:
            account_id = (
                product.property_account_expense_id.id
                or product.categ_id.property_account_expense_categ_id.id
            )
        if not account_id:
            raise UserError(
                _(
                    "There is no purchase account defined for this product: %s."
                    "\nYou may have to install a chart of account from "
                    "Accounting app, settings menu."
                ) % (product.name,)
            )

        zero_dp_orders = self.advance_line.filtered(lambda x: x.dp_order == 0) 
        if zero_dp_orders:
            raise UserError(
                f"The value of the order down payment {zero_dp_orders.mapped('purchase_id.name')} amount must be positive."
            )

        for ad_line in self.advance_line:
            if ad_line.dp_order == 0:
                raise UserError(
                    f"The value of the order down payment {ad_line.purchase_id.name} amount must be positive."
                )

        # Cache data for faster access
        advance_line_mapping = {
            line.purchase_id.id: line for line in self.advance_line
        }
        po_line_mapping = {
            line.order_id.id: line for line in po_lines
        }

        taxes = product.supplier_taxes_id.filtered(
            lambda r: not orders.mapped('company_id') or r.company_id.id == orders.mapped('company_id.id')[0]
        )
        tax_ids = (
            orders.mapped('fiscal_position_id').map_tax(taxes).ids
            if orders.mapped('fiscal_position_id') and taxes else taxes.ids
        )

        # Prepare product line items
        product_line_ids = [
            (
                0,
                0,
                {
                    "name": order.name,
                    "account_id": order.product_id.product_tmpl_id.get_product_accounts(
                        fiscal_pos=order.order_id.fiscal_position_id
                    ).get('expense').id,
                    "price_unit": order.price_unit,
                    "quantity": order.qty_received,
                    "product_uom_id": order.product_uom.id,
                    "product_id": order.product_id.id,
                    "purchase_line_id": order.id,
                    "tax_ids": [(6, 0, order.taxes_id.ids)],
                },
            )
            for order in orders.order_line.filtered(lambda x: not x.is_deposit and not x.is_downpayment)
        ]

        # Prepare deposit line items
        deposit_line_ids = []
        for order in orders:
            advance_line = advance_line_mapping.get(order.id)
            po_line = po_line_mapping.get(order.id)

            if advance_line and po_line:
                price_unit = (
                    advance_line.dp_order
                    if self.advance_payment_method == 'fixed'
                    else advance_line.dp_order * advance_line.dp_blanket
                )
                deposit_line_ids.append(
                    (
                        0,
                        0,
                        {
                            "name": order.name,
                            "account_id": account_id,
                            "price_unit": price_unit,
                            "quantity": -1.0,
                            "product_uom_id": product.uom_id.id,
                            "product_id": product.id,
                            "purchase_line_id": po_line.id,
                            "tax_ids": [(6, 0, tax_ids)],
                            "is_downpayment": True,
                        },
                    )
                )

        # Combine product and deposit lines
        invoice_line_ids = deposit_line_ids + product_line_ids
        deposit_val = {
            "invoice_origin": ', '.join(orders.mapped('name')),
            "move_type": "in_invoice",
            "partner_id": orders.mapped('partner_id').id,
            "invoice_line_ids": invoice_line_ids,
            "currency_id": orders.mapped('currency_id').id,
            "fiscal_position_id": orders.mapped('fiscal_position_id').id
                                or orders.mapped('partner_id').property_account_position_id.id,
        }

        return deposit_val

    def _prepare_deposit_val(self, order, po_line):
        # ir_property_obj = self.env["ir.property"]
        account_id = False
        product = self.purchase_deposit_product_id
        if product.id:
            account_id = (
                    product.property_account_expense_id.id
                    or product.categ_id.property_account_expense_categ_id.id
            )
        if not account_id:
            raise UserError(
                _(
                    "There is no purchase account defined for this product: %s."
                    "\nYou may have to install a chart of account from "
                    "Accounting app, settings menu."
                )
                % (product.name,)
            )

        if self.amount <= 0:
            raise UserError(_("The value of the deposit must be positive."))

        context = {"lang": order.partner_id.lang}
        amount = self.amount
        if self.advance_payment_method == "percentage":  # Case percent
            if self.amount > 100:
                raise UserError(_("The percentage of the deposit must be not over 100"))
            amount = self.amount / 100 * order.amount_untaxed

        name = _("Deposit Payment")
        del context
        taxes = product.supplier_taxes_id.filtered(
            lambda r: not order.company_id or r.company_id == order.company_id
        )
        if order.fiscal_position_id and taxes:
            tax_ids = order.fiscal_position_id.map_tax(taxes).ids
        else:
            tax_ids = taxes.ids

        deposit_val = {
            "is_deposit": True if self.amount > 0 else False,
            "invoice_origin": order.name,
            "move_type": "in_invoice",
            "partner_id": order.partner_id.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": name,
                        "account_id": account_id,
                        "price_unit": amount,
                        "quantity": 1.0,
                        "product_uom_id": product.uom_id.id,
                        "product_id": product.id,
                        "purchase_line_id": po_line.id,
                        "tax_ids": [(6, 0, tax_ids)],
                        "analytic_distribution": po_line.analytic_distribution,
                        # "is_downpayment": True
                        "is_deposit": True
                    },
                )
            ],
            "currency_id": order.currency_id.id,
            "invoice_payment_term_id": order.payment_term_id.id,
            "fiscal_position_id": order.fiscal_position_id.id
                                  or order.partner_id.property_account_position_id.id,
            "purchase_id": order.id,
            "narration": order.notes,
        }
        return deposit_val

    def _create_invoice(self, order, po_line):
        Invoice = self.env["account.move"]
        
        # BATCH
        if self.count > 1:
            deposit_val = self._prepare_deposit_val_batch(order, po_line)
        # BATCH
        else:

            deposit_val = self._prepare_deposit_val(order, po_line)
        
        invoice = Invoice.create(deposit_val)
        invoice.message_post_with_source(
            "mail.message_origin_link",
            render_values={"self": invoice, "origin": order},
            subtype_xmlid="mail.mt_note",
        )
        return invoice

    def _prepare_advance_purchase_line(self, order, product, tax_ids, amount = False):
        # BATCH
        if self.count > 1:
            return [
                {
                "name": _("Advance: %s") % (time.strftime("%m %Y"),),
                # "price_unit": amount,
                "price_unit": 0,
                # "product_qty": 0.0,
                "product_qty": 1.0,
                "order_id": o.id,
                "product_uom": product.uom_id.id,
                "product_id": product.id,
                "taxes_id": [(6, 0, tax_ids)],
                "date_planned": datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                # "is_deposit": True,
                "is_deposit": True if self.amount > 0 else False,
                "is_downpayment": True if self.amount == 0 else False
                
                } for o in order
            ]
        # BATCH
        else:
            return {
                "name": _("Advance: %s") % (time.strftime("%m %Y"),),
                # "price_unit": amount,
                "price_unit": 0,
                # "product_qty": 0.0,
                "product_qty": 1.0,
                "order_id": order.id,
                "product_uom": product.uom_id.id,
                "product_id": product.id,
                "taxes_id": [(6, 0, tax_ids)],
                "date_planned": datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                # "is_deposit": True,
                "is_deposit": True if self.amount > 0 else False,
                "is_downpayment": True if self.amount == 0 else False
            }

    def create_invoices(self):
        Purchase = self.env["purchase.order"]
        purchases = Purchase.browse(self._context.get("active_ids", []))


        # if len(purchases) == 1 and self.amount > 0:
        #     amount = self.amount
        #     if self.advance_payment_method == "percentage":  # Case percent
        #         amount = self.amount / 100 * purchases.amount_untaxed
        #     purchases.write({
        #         'dp_blanket' : purchases.dp_blanket + amount
        #     })

        # Create deposit product if necessary
        product = self.purchase_deposit_product_id
        if not product:
            vals = self._prepare_deposit_product()
            product = self.purchase_deposit_product_id = self.env["product.product"].create(vals)
            self.env.company.purchase_deposit_product_id = product

        if product.purchase_method != "purchase":
                raise UserError(
                    _(
                        "The product used to invoice a down payment should have "
                        'an invoice policy set to "Ordered quantities". '
                        "Please update your deposit product to be able to "
                        "create a deposit invoice."
                    )
                )
        if product.type != "service":
            raise UserError(
                _(
                    "The product used to invoice a down payment should be "
                    'of type "Service". Please use another product or '
                    "update this product."
                )
            )

        PurchaseLine = self.env["purchase.order.line"]
        # Menambahkan validasi DP
        for order in purchases:
            # Hitung jumlah yang akan diinvoice
            if self.advance_payment_method == "percentage":
                amount = self.amount / 100 * order.amount_untaxed
            else:
                amount = self.amount

            # VALIDASI: Jika amount melebihi total PO
            if amount > order.amount_total:
                raise UserError(_(
                    "The deposit amount exceeds the total order amount."
                ))
        
        if self.count > 1: 
            self._process_create_invoices_dp(purchases, product, PurchaseLine)
        else:
            for order in purchases:
                amount = self.amount
                if self.advance_payment_method == "percentage":  # Case percent
                    amount = self.amount / 100 * order.amount_untaxed

                # Set dp_blanket on the purchase order
                # order.dp_blanket = amount
                # order.dp_blanket = order.dp_blanket + amount

                # if product.purchase_method != "purchase":
                #     raise UserError(
                #         _(
                #             "The product used to invoice a down payment should have "
                #             'an invoice policy set to "Ordered quantities". '
                #             "Please update your deposit product to be able to "
                #             "create a deposit invoice."
                #         )
                #     )
                # if product.type != "service":
                #     raise UserError(
                #         _(
                #             "The product used to invoice a down payment should be "
                #             'of type "Service". Please use another product or '
                #             "update this product."
                #         )
                #     )

                taxes = product.supplier_taxes_id.filtered(
                    lambda r, order=order: not order.company_id
                                        or r.company_id == order.company_id
                )
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                else:
                    tax_ids = taxes.ids

                context = {"lang": order.partner_id.lang}
                adv_po_line_dict = self._prepare_advance_purchase_line(
                    order, product, tax_ids, amount
                )
                
                po_line = PurchaseLine.create(adv_po_line_dict)
                del context
                inv = self._create_invoice(order, po_line)
                
                po_line.write({"move_id": inv.id})
                
                if self._context.get("open_bills", False):
                    return purchases.action_view_invoice()

        return {"type": "ir.actions.act_window_close"}

    def _prepare_deposit_product(self):
        return {
            "name": "Purchase Deposit",
            "type": "service",
            "purchase_method": "purchase",
            "property_account_expense_id": self.deposit_account_id.id,
            "supplier_taxes_id": [(6, 0, self.deposit_taxes_id.ids)],
            "company_id": False,
        }
    
    def _process_create_invoices_dp(self, purchases, product, PurchaseLine):
        # for order in purchases:
            
            # amount = self.amount
            # if self.advance_payment_method == "percentage":  # Case percent
            #     amount = self.amount / 100 * order.amount_untaxed

            # Set dp_blanket on the purchase order
            # order.dp_blanket = amount
            # order.dp_blanket = order.dp_blanket + amount

        taxes = product.supplier_taxes_id.filtered(
            lambda r: not purchases.mapped('company_id')
                                or r.company_id == purchases.mapped('company_id').id
        )
        if purchases.mapped('fiscal_position_id') and taxes:
            tax_ids = purchases.mapped('fiscal_position_id').map_tax(taxes).ids
        else:
            tax_ids = taxes.ids

        context = {"lang": purchases.mapped('partner_id.lang')}
        
        adv_po_line_dict = self._prepare_advance_purchase_line(
            purchases, product, tax_ids
        )
        
        po_lines = PurchaseLine.create(adv_po_line_dict)

        del context
        inv = self._create_invoice(purchases, po_lines)
        
        # po_line.write({"move_id": inv.id})
        for pl in po_lines:
            pl.write({
                "move_id": inv.id
            })
        
        if self._context.get("open_bills", False):
            return purchases[0].action_view_invoice()

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get("active_model", [])
        active_ids = self.env.context.get("active_ids", [])
        if active_model == 'purchase.order':
            orders = self.env[active_model].browse(active_ids)
            if len(orders.mapped("partner_id")) > 1:
                raise UserError(_("Please select one vendor at a time"))
            res["advance_line"] = [
                (
                    0,
                    0,
                    {
                        "purchase_id": line.id,
                        "dp_sisa": line.dp_sisa,
                    },
                )
                for line in orders
            ]
        return res
