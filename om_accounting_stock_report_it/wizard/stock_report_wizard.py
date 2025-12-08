from odoo import models, fields, api
from collections import defaultdict


class StockReportWizard(models.TransientModel):
    _name = 'stock.report.wizard'
    _description = 'Stock Report Wizard'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    product_ids = fields.Many2many('product.product', string="Products")
    category_ids = fields.Many2many('product.category', string="Product Categories")

    def action_confirm(self):
        self.ensure_one()

        StockValuationLayer = self.env['stock.valuation.layer']
        Product = self.env['product.product']

        # Hapus data sebelumnya
        self.env['stock.report.line'].search([]).unlink()

        # Filter produk sesuai input wizard
        if self.product_ids:
            products = self.product_ids
        elif self.category_ids:
            products = Product.search([('categ_id', 'in', self.category_ids.ids)])
        else:
            products = Product.search([])

        # Dictionary penyimpanan data
        report_data = defaultdict(lambda: {
            'opening_qty': 0.0,
            'opening_value': 0.0,
            'qty_in': 0.0,
            'value_in': 0.0,
            'qty_out': 0.0,
            'value_out': 0.0,
            'uom_id': False,
            'currency_id': False,
            'product_id': False,
            'category_id': False,
            'unit_price': 0.0
        })

        # === OPENING BALANCE (sebelum date_from)
        opening_domain = [
            ('product_id', 'in', products.ids),
            '|', '|',
            '&', ('accounting_date', '<', self.date_from), ('accounting_date', '!=', False),
            '&', ('date_inventory', '<', self.date_from), ('date_inventory', '!=', False),
            '&', ('date_manufacturing', '<', self.date_from), ('date_manufacturing', '!=', False),
        ]
        opening_layers = StockValuationLayer.search(opening_domain)

        for line in opening_layers:
            key = line.product_id.id
            report_data[key]['opening_qty'] += line.quantity
            report_data[key]['opening_value'] += line.value
            report_data[key]['product_id'] = line.product_id.id
            report_data[key]['category_id'] = line.product_id.categ_id.id
            report_data[key]['uom_id'] = line.uom_id.id
            report_data[key]['currency_id'] = line.currency_id.id or self.env.company.currency_id.id

        # === TRANSAKSI DALAM PERIODE
        range_domain = [
            ('product_id', 'in', products.ids),
            '|', '|',
            '&', ('accounting_date', '>=', self.date_from), ('accounting_date', '<=', self.date_to),
            '&', ('date_inventory', '>=', self.date_from), ('date_inventory', '<=', self.date_to),
            '&', ('date_manufacturing', '>=', self.date_from), ('date_manufacturing', '<=', self.date_to),
        ]
        range_layers = StockValuationLayer.search(range_domain)

        for line in range_layers:
            key = line.product_id.id
            report_data[key]['product_id'] = line.product_id.id
            report_data[key]['category_id'] = line.product_id.categ_id.id
            report_data[key]['uom_id'] = line.uom_id.id
            report_data[key]['currency_id'] = line.currency_id.id or self.env.company.currency_id.id

            if line.value >= 0:
                report_data[key]['qty_in'] += line.quantity
                report_data[key]['value_in'] += line.value
            else:
                report_data[key]['qty_out'] += abs(line.quantity)
                report_data[key]['value_out'] += abs(line.value)

            report_data[key]['unit_price'] = abs(line.unit_cost)

        # Simpan ke stock.report.line
        for data in report_data.values():
            closing_qty = data['opening_qty'] + data['qty_in'] - data['qty_out']
            closing_value = data['opening_value'] + data['value_in'] - data['value_out']

            self.env['stock.report.line'].create({
                'product_id': data['product_id'],
                'category_id': data['category_id'],
                'uom_id': data['uom_id'],
                'currency_id': data['currency_id'],
                'opening_qty': data['opening_qty'],
                'opening_value': data['opening_value'],
                'qty_in': data['qty_in'],
                'value_in': data['value_in'],
                'qty_out': data['qty_out'],
                'value_out': data['value_out'],
                'closing_qty': closing_qty,
                'closing_value': closing_value,
                'unit_price': data['unit_price'],
                'date_from': self.date_from,
                'date_to': self.date_to,
            })

        # Tampilkan hasil
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Report',
            'view_mode': 'list',
            'res_model': 'stock.report.line',
            'target': 'current',
            'domain': [('product_id', 'in', products.ids)],
        }
