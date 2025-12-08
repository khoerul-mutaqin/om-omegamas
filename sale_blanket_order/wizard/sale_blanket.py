# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_blanket_order_ids = fields.Many2many(
        'sale.blanket.order',
        'account_move_sale_blanket_order_rel',
        'account_move_id',
        string="Sale Blanket Order"
    )

class SaleBlanketAdvancePaymentInv(models.TransientModel):
    _name = 'sale.blanket.advance.payment.inv'
    _description = "Sales Blanket Advance Payment Invoice"

    advance_payment_method = fields.Selection(
        selection=[
            # ('delivered', "Regular invoice"),
            ('percentage', "Down payment (percentage)"),
            ('fixed', "Down payment (fixed amount)"),
        ],
        string="Create Invoice",
        default='fixed',
        required=True,
        help="A standard invoice is issued with all the order lines ready for invoicing,"
            "according to their invoicing policy (based on ordered or delivered quantity).")
    count = fields.Integer(string="Order Count", compute='_compute_count')
    sale_blanket_order_ids = fields.Many2many(
        'sale.blanket.order', default=lambda self: self.env.context.get('active_ids'))

    # Down Payment logic
    has_down_payments = fields.Boolean(
        string="Has down payments", compute="_compute_has_down_payments")
    deduct_down_payments = fields.Boolean(string="Deduct down payments", default=True)

    # New Down Payment
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Down Payment Product",
        domain=[('type', '=', 'service')],
        compute='_compute_product_id',
        readonly=False,
        store=True)
    amount = fields.Float(
        string="Down Payment Amount",
        help="The percentage of amount to be invoiced in advance.")
    fixed_amount = fields.Monetary(
        string="Down Payment Amount (Fixed)",
        help="The fixed amount to be invoiced in advance.")
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
        store=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        compute='_compute_company_id',
        store=True)
    amount_invoiced = fields.Monetary(
        string="Already invoiced",
        compute="_compute_invoice_amounts",
        help="Only confirmed down payments are considered.")
    amount_to_invoice = fields.Monetary(
        string="Amount to invoice",
        compute="_compute_invoice_amounts",
        help="The amount to invoice = Sale Order Total - Confirmed Down Payments.")

    # Only used when there is no down payment product available
    #  to setup the down payment product
    deposit_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Income Account",
        domain=[('deprecated', '=', False)],
        check_company=True,
        help="Account used for deposits")
    deposit_taxes_id = fields.Many2many(
        comodel_name='account.tax',
        string="Customer Taxes",
        domain=[('type_tax_use', '=', 'sale')],
        check_company=True,
        help="Taxes used for deposits")

    # UI
    display_draft_invoice_warning = fields.Boolean(compute="_compute_display_draft_invoice_warning")
    display_invoice_amount_warning = fields.Boolean(compute="_compute_display_invoice_amount_warning")
    consolidated_billing = fields.Boolean(
        string="Consolidated Billing", default=True,
        help="Create one invoice for all orders related to same customer and same invoicing address"
    )

    #=== COMPUTE METHODS ===#

    @api.depends('sale_blanket_order_ids')
    def _compute_count(self):
        for wizard in self:
            wizard.count = len(wizard.sale_blanket_order_ids)

    @api.depends('sale_blanket_order_ids')
    def _compute_has_down_payments(self):
        for wizard in self:
            wizard.has_down_payments = bool(
                wizard.sale_blanket_order_ids.line_ids.filtered('is_downpayment')
            )

    # next computed fields are only used for down payments invoices and therefore should only
    # have a value when 1 unique SO is invoiced through the wizard
    @api.depends('sale_blanket_order_ids')
    def _compute_currency_id(self):
        self.currency_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.currency_id = wizard.sale_blanket_order_ids.currency_id

    @api.depends('sale_blanket_order_ids')
    def _compute_company_id(self):
        self.company_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.company_id = wizard.sale_blanket_order_ids.company_id

    @api.depends('company_id')
    def _compute_product_id(self):
        self.product_id = False
        for wizard in self:
            if wizard.count == 1:
                wizard.product_id = wizard.company_id.sale_down_payment_product_id

    @api.depends('amount', 'fixed_amount', 'advance_payment_method', 'amount_to_invoice')
    def _compute_display_invoice_amount_warning(self):
        for wizard in self:
            invoice_amount = wizard.fixed_amount
            if wizard.advance_payment_method == 'percentage':
                invoice_amount = wizard.amount / 100 * sum(wizard.sale_blanket_order_ids.mapped('amount_total'))
            wizard.display_invoice_amount_warning = invoice_amount > wizard.amount_to_invoice

    @api.depends('sale_blanket_order_ids')
    def _compute_display_draft_invoice_warning(self):
        for wizard in self:
            wizard.display_draft_invoice_warning = wizard.sale_blanket_order_ids.invoice_ids.filtered(lambda invoice: invoice.state == 'draft')

    @api.depends('sale_blanket_order_ids')
    def _compute_invoice_amounts(self):
        for wizard in self:
            wizard.amount_invoiced = sum(wizard.sale_blanket_order_ids._origin.mapped('amount_invoiced'))
            wizard.amount_to_invoice = sum(wizard.sale_blanket_order_ids._origin.mapped('amount_to_invoice'))

    #=== ONCHANGE METHODS ===#

    @api.onchange('advance_payment_method')
    def _onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            amount = self.default_get(['amount']).get('amount')
            return {'value': {'amount': amount}}

    #=== CONSTRAINT METHODS ===#

    def _check_amount_is_positive(self):
        for wizard in self:
            if wizard.advance_payment_method == 'percentage' and wizard.amount <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))
            elif wizard.advance_payment_method == 'fixed' and wizard.fixed_amount <= 0.00:
                raise UserError(_('The value of the down payment amount must be positive.'))

    @api.constrains('product_id')
    def _check_down_payment_product_is_valid(self):
        for wizard in self:
            if wizard.count > 1 or not wizard.product_id:
                continue
            if wizard.product_id.invoice_policy != 'order':
                raise UserError(_(
                    "The product used to invoice a down payment should have an invoice policy"
                    "set to \"Ordered quantities\"."
                    " Please update your deposit product to be able to create a deposit invoice."))
            if wizard.product_id.type != 'service':
                raise UserError(_(
                    "The product used to invoice a down payment should be of type 'Service'."
                    " Please use another product or update this product."))

    #=== ACTION METHODS ===#

    def create_invoices(self):
        self._check_amount_is_positive()
        sale_blanket_order_ids = self.env['sale.blanket.order'].browse(self._context.get('active_ids'))
        for order in sale_blanket_order_ids:
            if self.advance_payment_method == 'fixed':
                order.down_payment = self.fixed_amount
            elif self.advance_payment_method == 'percentage':
                order.down_payment = (self.amount / 100.0) * order.amount_total

            # Validasi: Jangan sampai total down_payment melebihi total order
            if order.down_payment > order.amount_total:
                raise UserError(_(
                    "The deposit amount exceeds the total order amount."
                ))
        invoices = self._create_invoices(self.sale_blanket_order_ids)
        return self.sale_blanket_order_ids.action_view_invoice(invoices=invoices)

#create jurnal dp di blanket
    def view_draft_invoices(self):
        return {
            'name': _('Draft Invoices'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'views': [(False, 'list'), (False, 'form')],
            'res_model': 'account.move',
            'domain': [('line_ids.sale_line_ids.order_id', 'in', self.sale_blanket_order_ids.ids), ('state', '=', 'draft')],
        }

    # === BUSINESS METHODS ===#

    def _create_invoices(self, sale_orders):
        self.ensure_one()

        self.sale_blanket_order_ids.ensure_one()
        self = self.with_company(self.company_id)
        order = self.sale_blanket_order_ids

        # Create deposit product if necessary
        if not self.product_id:
            self.company_id.sudo().sale_down_payment_product_id = self.env['product.product'].create(
                self._prepare_down_payment_product_values()
            )
            self._compute_product_id()



        invoice = self.env['account.move'].sudo().create(
            self._prepare_invoice_values(order)
        )

        # Ensure the invoice total is exactly the expected fixed amount.
        if self.advance_payment_method == 'fixed':
            delta_amount = (invoice.amount_total - self.fixed_amount) * (1 if invoice.is_inbound() else -1)
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

        # Unsudo the invoice after creation if not already sudoed
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

    def _prepare_down_payment_product_values(self):
        self.ensure_one()
        return {
            'name': _('Down payment'),
            'type': 'service',
            'invoice_policy': 'order',
            'company_id': self.company_id.id,
            'property_account_income_id': self.deposit_account_id.id,
            'taxes_id': [Command.set(self.deposit_taxes_id.ids)],
        }

    def _prepare_down_payment_section_values(self, order):
        context = {'lang': order.partner_id.lang}

        so_values = {
            'name': _('Down Payments'),
            'product_uom_qty': 0.0,
            'order_id': order.id,
            'display_type': 'line_section',
            'is_downpayment': True,
            'sequence': order.line_ids and order.line_ids[-1].sequence + 1 or 10,
        }

        del context
        return so_values



    def _prepare_invoice_values(self, order):
        
        global price_unit
        self.ensure_one()
        # Prepare the base invoice values
        invoice_values = order._prepare_invoice()

        # Create invoice line values
        invoice_line_ids = []

        for line in order:
            if self.advance_payment_method == 'fixed':
                price_unit = self.fixed_amount
            elif self.advance_payment_method == 'percentage':
                price_unit = (self.amount / 100.0) * order.amount_total
            # Manually prepare the line values
            line_values = {
                'product_id': line.company_id.sale_down_payment_product_id.id,
                'price_unit': price_unit,
                'quantity': 1.0,
                # 'discount': line.discount,
                # 'tax_ids': [(6, 0, line.taxes_id.ids)],
                # 'analytic_distribution': line.analytic_distribution,
                'account_id': line.company_id.sale_down_payment_product_id.property_account_income_id.id,
                # 'analytic_account_id': order.analytic_account_id.id if order.analytic_account_id else False,
                'product_uom_id': line.company_id.sale_down_payment_product_id.uom_id.id,
                # 'name': self._get_down_payment_description(order) or line.product_id.name,
            }

            # Append the prepared line values to the invoice line list
            invoice_line_ids.append(Command.create(line_values))

        # Update the invoice values with the line IDs
        invoice_values['invoice_line_ids'] = invoice_line_ids
        return invoice_values

    def _get_down_payment_description(self, order):
        self.ensure_one()
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            name = _("Down payment of %s%%", self.amount)
        else:
            name = _('Down Payment')
        del context
        return name

