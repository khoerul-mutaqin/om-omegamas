# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    symbol = fields.Char(related='currency_id.symbol', readonly=True)

    dp_blanket = fields.Float('Down Payment')
    dp_order = fields.Float(string="Order Down Payment")
    dp_sisa = fields.Float(string="Remaining Down Payment")
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Down Payment Product",
        domain=[('type', '=', 'service')],
        compute='_compute_product_id',
        readonly=False,
        store=True)
    advance_line = fields.One2many('sale.advance.payment.inv.line', 'advance_payment_id')

    @api.depends('company_id')
    def _compute_product_id(self):
        self.product_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.product_id = wizard.company_id.sale_down_payment_product_id

    def _check_amount_is_positive(self):
        for wizard in self:
            if wizard.dp_order <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))

    def create_invoices(self):
        if self.count > 1 and self.advance_payment_method != 'delivered':
            for rec in self.advance_line:
                if rec.dp_blanket and rec.dp_order > rec.dp_sisa:
                    raise UserError(f'''Order Down Payment {rec.sale_id.name} Exceeding Remaining Down Payment''')
                if rec.dp_blanket and rec.dp_order == 0.00:
                    raise UserError(f'''The value of the order down payment {rec.sale_id.name} amount must be positive.''')
        if self.count == 1 and self.advance_payment_method != 'delivered':
            if self.dp_blanket and self.dp_order > self.dp_sisa:
                raise UserError("Order Down Payment Exceeding Remaining Down Payment")
            if self.dp_order == 0.00:
                raise UserError(_('The value of the order down payment amount must be positive.'))
        invoices = self._create_invoices(self.sale_order_ids)
        # Create account di journal
        account_debit = self.env['account.account'].search([('code', '=', '510101')], limit=1)
        account_credit = self.env['account.account'].search([('code', '=', '120603')], limit=1)
        
        if not account_debit or not account_credit:
            raise UserError("Account tidak ditemukan. Periksa konfigurasi akun!")

        for invoice in invoices:
            for line in invoice.invoice_line_ids:
                product = line.product_id
                sale_line = line.sale_line_ids[:1]
                if not sale_line or not product:
                    continue
                
                # Ambil stock moves yang done dan produk sama
                moves = sale_line.move_ids.filtered(lambda m: m.state == 'done' and m.product_id == product)
                
                for move in moves:
                    valuation_layers = move.stock_valuation_layer_ids
                    for valuation in valuation_layers:
                        val = abs(valuation.value)  # jadikan positif
                        
                        # Buat journal items
                        self.env['account.move.line'].create({
                            'move_id': invoice.id,
                            'account_id': account_debit.id,
                            'name': line.name,
                            'debit': val,
                            'credit': 0,
                        })

                        self.env['account.move.line'].create({
                            'move_id': invoice.id,
                            'account_id': account_credit.id,
                            'name': line.name,
                            'debit': 0,
                            'credit': val,
                        })
        return self.sale_order_ids.action_view_invoice(invoices=invoices)

    def _prepare_invoice_values(self, order, so_lines, accounts):
        self.ensure_one()
        lines = []
        for line, account in zip(so_lines, accounts):
            if not line.display_type and not line.is_downpayment:
                qty_invoice = (line.qty_delivered if line.qty_delivered else line.product_uom_qty) if line.qty_invoiced == 0 else line.qty_delivered - line.qty_invoiced
                # BATCH
                if self.count > 1:
                    lines.append(Command.create(
                        line._prepare_invoice_line(
                            name=line.product_id.name,
                            quantity=qty_invoice,
                            **({'account_id': account['account'].id} if account['account'] else {}),
                        )
                    ))
                # BATCH
                else:
                    lines.append(Command.create(
                        line._prepare_invoice_line(
                            name=line.product_id.name,
                            quantity=qty_invoice,
                            **({'account_id': account.id} if account else {}),
                        )
                    ))
            else: 
                account_dp = self.env.company.sale_down_payment_product_id.property_account_income_id
                # BATCH
                if self.count > 1:
                    lines.append(Command.create(
                        line._prepare_invoice_line(
                            name=self._get_down_payment_description(order),
                            quantity=1.0,
                            price_unit= -(line.price_unit),
                            **({'account_id': account_dp.id} if account_dp.id else {}),
                        )
                    ))
                # BATCH
                else:
                    lines.append(Command.create(
                        line._prepare_invoice_line(
                            name=self._get_down_payment_description(order[0]),
                            quantity=1.0,
                            price_unit= -(line.price_unit),
                            **({'account_id': account_dp.id} if account_dp.id else {}),
                        )
                    ))
        if self.count > 1:
            return {
                **order[0]._prepare_invoice(),
                'invoice_line_ids': lines
            }
        else:
            return {
                **order._prepare_invoice(),
                'invoice_line_ids': lines
            }

    def _create_invoices(self, sale_orders):
        self.ensure_one()
        if self.advance_payment_method == 'delivered':
            if sum(sale_orders.mapped('dp_blanket')) > 0:
                return sale_orders._create_invoices(final=False, grouped=not self.consolidated_billing)
            return sale_orders._create_invoices(final=self.deduct_down_payments, grouped=not self.consolidated_billing)
        else:
            # BATCH INV
            if self.count > 1:
                return self._create_batch_invoices(sale_orders)
            # BATCH INV
            else:
                self.sale_order_ids.ensure_one()
                self = self.with_company(self.company_id)
                dp_order = self.dp_order
                order = self.sale_order_ids
                # Create down payment section if necessary
                SaleOrderline = self.env['sale.order.line'].with_context(sale_no_log_for_new_lines=True)

                if not any(line.display_type and line.is_downpayment for line in order.order_line):
                    SaleOrderline.create(
                        self._prepare_down_payment_section_values(order)
                    )
                values, accounts = self._prepare_down_payment_lines_values(order)
                # down_payment_lines = SaleOrderline.create(values)
                down_payment_lines = SaleOrderline.create(values[order.id])


                line_ex_dp = order.order_line.filtered(lambda l: not l.display_type and not l.is_downpayment)
                down_payment_lines |=  line_ex_dp
                # if len(accounts) < len(down_payment_lines):
                #     for a in down_payment_lines:
                #         accounts += accounts
                accounts = [accounts[i % len(accounts)] for i in range(len(down_payment_lines))]



                invoice = self.env['account.move'].sudo().create(
                    self._prepare_invoice_values(order, down_payment_lines, accounts)
                )
                if self.advance_payment_method == 'fixed':
                    # delta_amount = (invoice.amount_total - self.fixed_amount) * (1 if invoice.is_inbound() else -1)
                    # delta_amount = (invoice.amount_total - self.dp_order)
                    delta_amount = (invoice.amount_total - dp_order)
                    if not order.currency_id.is_zero(delta_amount):
                        receivable_line = invoice.line_ids\
                            .filtered(lambda aml: aml.account_id.account_type == 'asset_receivable')[:1]
                        product_lines = invoice.line_ids\
                            .filtered(lambda aml: aml.display_type == 'product')
                        tax_lines = invoice.line_ids\
                            .filtered(lambda aml: aml.tax_line_id.amount_type not in (False, 'fixed'))

                        if product_lines and tax_lines and receivable_line:
                            line_commands = [Command.update(receivable_line.id, {
                                'amount_currency': receivable_line.amount_currency + delta_amount,
                            })]
                            delta_sign = 1 if delta_amount > 0 else -1
                            for lines, attr, sign in (
                                (product_lines, 'price_total', -1),
                                (tax_lines, 'amount_currency', 1),
                            ):
                                remaining = delta_amount
                                lines_len = len(lines)
                                for line in lines:
                                    if order.currency_id.compare_amounts(remaining, 0) != delta_sign:
                                        break
                                    amt = delta_sign * max(
                                        order.currency_id.rounding,
                                        abs(order.currency_id.round(remaining / lines_len)),
                                    )
                                    remaining -= amt
                                    line_commands.append(Command.update(line.id, {attr: line[attr] + amt * sign}))
                            invoice.line_ids = line_commands

                invoice = invoice.sudo(self.env.su)
                poster = self.env.user._is_internal() and self.env.user.id or SUPERUSER_ID
                invoice.with_user(poster).message_post_with_source(
                    'mail.message_origin_link',
                    render_values={'self': invoice, 'origin': order},
                    subtype_xmlid='mail.mt_note',
                )

                title = _("Down payment invoice")
                order.with_user(poster).message_post(
                    body=_("%s has been created", invoice._get_html_link(title=title)),
                )

                return invoice

    def _create_batch_invoices(self, sale_orders):
        # dp_order = self.advance_line.filtered(lambda x: x.sale_id.id == order.id).dp_order
        dp_order = sum([x.dp_order for x in self.advance_line])
        order = sale_orders
        SaleOrderline = self.env['sale.order.line'].with_context(sale_no_log_for_new_lines=True)

        # BATCH INV

        for o in order:
            if not any(line.display_type and line.is_downpayment for line in o.order_line):
                SaleOrderline |= SaleOrderline.create(
                    self._prepare_down_payment_section_values(o)
                )
        # BATCH INV

        values, accounts = self._prepare_down_payment_lines_values_batch(order)

        # flattened_values = [item for sublist in values for item in sublist]
        # flattened_values = [sublist.values() for sublist in values]
        flattened_values = [list(sublist.values())[0] for sublist in values]
        down_payment_lines = SaleOrderline.create(flattened_values)

        line_ex_dp = order.order_line.filtered(lambda l: not l.display_type and not l.is_downpayment)
        down_payment_lines |= line_ex_dp

        # flattened_accounts = [item for sublist in accounts for item in sublist]
        flattened_accounts = [acc for acc in accounts]
        list_account = []
        if len(flattened_accounts) < len(down_payment_lines):
            # for a in down_payment_lines:
            #     flattened_accounts += flattened_accounts
            for dpl in down_payment_lines:
                # list_account.extend([x for x in flattened_accounts if x['order_id'] == dpl.order_id.id])
                list_account.extend([x for x in flattened_accounts if x['order_id'] == dpl.order_id.id])

        invoice = self.env['account.move'].sudo().create(
            self._prepare_invoice_values(order, down_payment_lines, list_account)
        )
        if self.advance_payment_method == 'fixed':
            # delta_amount = (invoice.amount_total - self.fixed_amount) * (1 if invoice.is_inbound() else -1)
            # delta_amount = (invoice.amount_total - self.dp_order)
            delta_amount = (invoice.amount_total - dp_order)
            if not order.currency_id.is_zero(delta_amount):
                receivable_line = invoice.line_ids \
                                      .filtered(lambda aml: aml.account_id.account_type == 'asset_receivable')[:1]
                product_lines = invoice.line_ids \
                    .filtered(lambda aml: aml.display_type == 'product')
                tax_lines = invoice.line_ids \
                    .filtered(lambda aml: aml.tax_line_id.amount_type not in (False, 'fixed'))

                if product_lines and tax_lines and receivable_line:
                    line_commands = [Command.update(receivable_line.id, {
                        'amount_currency': receivable_line.amount_currency + delta_amount,
                    })]
                    delta_sign = 1 if delta_amount > 0 else -1
                    for lines, attr, sign in (
                            (product_lines, 'price_total', -1),
                            (tax_lines, 'amount_currency', 1),
                    ):
                        remaining = delta_amount
                        lines_len = len(lines)
                        for line in lines:
                            if order.currency_id.compare_amounts(remaining, 0) != delta_sign:
                                break
                            amt = delta_sign * max(
                                order.currency_id.rounding,
                                abs(order.currency_id.round(remaining / lines_len)),
                            )
                            remaining -= amt
                    line_commands.append(Command.update(line.id, {attr: line[attr] + amt * sign}))
                    invoice.line_ids = line_commands

        return invoice
    # ODOO18 VERSION
    def _prepare_down_payment_lines_values(self, order):
        """ Create one down payment line per tax or unique taxes combination and per account.
            Apply the tax(es) to their respective lines.

            :param order: Order for which the down payment lines are created.
            :return:      An array of dicts with the down payment lines values.
        """
        self.ensure_one()

        price_unit = self.dp_order
        # dp_blanket = self.dp_blanket
        dp_blanket = self.dp_sisa
        amount = self.amount
        fixed_amount = self.fixed_amount


        if self.advance_payment_method == 'percentage':
            price_unit = price_unit * dp_blanket

        AccountTax = self.env['account.tax']

        if self.advance_payment_method == 'percentage':
            ratio = amount / 100
        else:
            ratio = fixed_amount / order.amount_total if order.amount_total else 1

        order_lines = order.order_line.filtered(lambda l: not l.display_type and not l.is_downpayment)
        down_payment_values = []
        for line in order_lines:
            base_line_values = line._prepare_base_line_for_taxes_computation(special_mode='total_excluded')
            product_account = line['product_id'].product_tmpl_id.get_product_accounts(fiscal_pos=order.fiscal_position_id)
            account = product_account.get('downpayment') or product_account.get('income')
            AccountTax._add_tax_details_in_base_line(base_line_values, order.company_id)
            tax_details = base_line_values['tax_details']

            taxes = line.tax_id.flatten_taxes_hierarchy()
            fixed_taxes = taxes.filtered(lambda tax: tax.amount_type == 'fixed')
            down_payment_values.append([
                taxes - fixed_taxes,
                base_line_values['analytic_distribution'],
                tax_details['raw_total_excluded_currency'],
                account,
            ])
            for fixed_tax in fixed_taxes:
                # Fixed taxes cannot be set as taxes on down payments as they always amounts to 100%
                # of the tax amount. Therefore fixed taxes are removed and are replace by a new line
                # with appropriate amount, and non fixed taxes if the fixed tax affected the base of
                # any other non fixed tax.
                if fixed_tax.price_include:
                    continue

                if fixed_tax.include_base_amount:
                    pct_tax = taxes[list(taxes).index(fixed_tax) + 1:]\
                        .filtered(lambda t: t.is_base_affected and t.amount_type != 'fixed')
                else:
                    pct_tax = self.env['account.tax']
                down_payment_values.append([
                    pct_tax,
                    base_line_values['analytic_distribution'],
                    base_line_values['quantity'] * fixed_tax.amount,
                    account
                ])

        downpayment_line_map = {}
        analytic_map = {}
        base_downpayment_lines_values = self._prepare_base_downpayment_line_values(order)
        for tax_id, analytic_distribution, price_subtotal, account in down_payment_values:
            grouping_key = frozendict({
                'tax_id': tuple(sorted(tax_id.ids)),
                'account_id': account,
            })
            downpayment_line_map.setdefault(grouping_key, {
                **base_downpayment_lines_values,
                'tax_id': grouping_key['tax_id'],
                'product_uom_qty': 0.0,
                'price_unit': 0.0,
            })
            # downpayment_line_map[grouping_key]['price_unit'] += price_unit
            downpayment_line_map[grouping_key]['price_unit'] = price_unit
            if analytic_distribution:
                analytic_map.setdefault(grouping_key, [])
                analytic_map[grouping_key].append((price_subtotal, analytic_distribution))

        # lines_values = []
        lines_values = {}
        accounts = []
        for key, line_vals in downpayment_line_map.items():
            # don't add line if price is 0 and prevent division by zero
            if order.currency_id.is_zero(line_vals['price_unit']):
                continue
            # weight analytic account distribution
            if analytic_map.get(key):
                line_analytic_distribution = {}
                for price_subtotal, account_distribution in analytic_map[key]:
                    for account, distribution in account_distribution.items():
                        line_analytic_distribution.setdefault(account, 0.0)
                        line_analytic_distribution[account] += price_subtotal / line_vals['price_unit'] * distribution
                line_vals['analytic_distribution'] = line_analytic_distribution
            # round price unit
            line_vals['price_unit'] = (order.currency_id.round(line_vals['price_unit']))

            # lines_values.append(line_vals)
            lines_values.update({line_vals['order_id']: line_vals})
            accounts.append(key['account_id'])

        return lines_values, accounts

    def _prepare_down_payment_lines_values_batch(self, orders):
        lines = []
        account_account = []
        for order in orders:
            line_advance = self.advance_line.filtered(lambda x: x.sale_id.id == order.id)
            price_unit = line_advance.dp_order
            # dp_blanket = line_advance.dp_blanket
            dp_sisa = line_advance.dp_sisa
            amount = line_advance.dp_order
            fixed_amount = line_advance.dp_order
            # BATCH INV

            if self.advance_payment_method == 'percentage':
                price_unit = price_unit * dp_sisa

            AccountTax = self.env['account.tax']

            if self.advance_payment_method == 'percentage':
                ratio = amount / 100
            else:
                ratio = fixed_amount / order.amount_total if order.amount_total else 1

            order_lines = order.order_line.filtered(lambda l: not l.display_type and not l.is_downpayment)
            down_payment_values = []
            for line in order_lines:
                base_line_values = line._prepare_base_line_for_taxes_computation(special_mode='total_excluded')
                product_account = line['product_id'].product_tmpl_id.get_product_accounts(fiscal_pos=order.fiscal_position_id)
                account = product_account.get('downpayment') or product_account.get('income')
                AccountTax._add_tax_details_in_base_line(base_line_values, order.company_id)
                tax_details = base_line_values['tax_details']

                taxes = line.tax_id.flatten_taxes_hierarchy()
                fixed_taxes = taxes.filtered(lambda tax: tax.amount_type == 'fixed')
                down_payment_values.append([
                    taxes - fixed_taxes,
                    base_line_values['analytic_distribution'],
                    tax_details['raw_total_excluded_currency'],
                    account,
                ])
                for fixed_tax in fixed_taxes:
                    # Fixed taxes cannot be set as taxes on down payments as they always amounts to 100%
                    # of the tax amount. Therefore fixed taxes are removed and are replace by a new line
                    # with appropriate amount, and non fixed taxes if the fixed tax affected the base of
                    # any other non fixed tax.
                    if fixed_tax.price_include:
                        continue

                    if fixed_tax.include_base_amount:
                        pct_tax = taxes[list(taxes).index(fixed_tax) + 1:]\
                            .filtered(lambda t: t.is_base_affected and t.amount_type != 'fixed')
                    else:
                        pct_tax = self.env['account.tax']
                    down_payment_values.append([
                        pct_tax,
                        base_line_values['analytic_distribution'],
                        base_line_values['quantity'] * fixed_tax.amount,
                        account
                    ])

            downpayment_line_map = {}
            analytic_map = {}
            base_downpayment_lines_values = self._prepare_base_downpayment_line_values(order)
            for tax_id, analytic_distribution, price_subtotal, account in down_payment_values:
                grouping_key = frozendict({
                    'tax_id': tuple(sorted(tax_id.ids)),
                    'account_id': account,
                })
                downpayment_line_map.setdefault(grouping_key, {
                    **base_downpayment_lines_values,
                    'tax_id': grouping_key['tax_id'],
                    'product_uom_qty': 0.0,
                    'price_unit': 0.0,
                })
                # downpayment_line_map[grouping_key]['price_unit'] += price_unit
                downpayment_line_map[grouping_key]['price_unit'] = price_unit
                if analytic_distribution:
                    analytic_map.setdefault(grouping_key, [])
                    analytic_map[grouping_key].append((price_subtotal, analytic_distribution))

            # lines_values = []
            # accounts = []
            lines_values = {}
            accounts = {}
            for key, line_vals in downpayment_line_map.items():
                # don't add line if price is 0 and prevent division by zero
                if order.currency_id.is_zero(line_vals['price_unit']):
                    continue
                # weight analytic account distribution
                if analytic_map.get(key):
                    line_analytic_distribution = {}
                    for price_subtotal, account_distribution in analytic_map[key]:
                        for account, distribution in account_distribution.items():
                            line_analytic_distribution.setdefault(account, 0.0)
                            line_analytic_distribution[account] += price_subtotal / line_vals['price_unit'] * distribution
                    line_vals['analytic_distribution'] = line_analytic_distribution
                # round price unit
                line_vals['price_unit'] = (order.currency_id.round(line_vals['price_unit']))

                lines_values.update({line_vals['order_id']: line_vals})
                accounts.update({'account': key['account_id'], 'order_id': line_vals['order_id']})
                # lines.append(line_vals)
                # accounts.append({'account': key['account_id'], 'order_id': line_vals['order_id']})
            lines.append(lines_values)
            account_account.append(accounts)
        # return lines_values, accounts
        return lines, account_account


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

       

        active_model = self.env.context.get("active_model", [])
        active_ids = self.env.context.get("active_ids", [])
        if active_model == 'sale.order':
            orders = self.env[active_model].browse(active_ids)
            if len(orders.mapped("partner_id")) > 1:
                raise UserError(_("Please select one customer at a time"))
            res["advance_line"] = [
                (
                    0,
                    0,
                    {
                        "sale_id": line.id,
                        # "dp_sisa": line.dp_sisa,
                    },
                )
                for line in orders
            ]
        return res
