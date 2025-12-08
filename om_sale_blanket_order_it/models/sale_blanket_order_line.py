from odoo import fields, models, api


class SaleBlanketOrderLine (models.Model):
    _inherit = 'sale.blanket.order.line'

    info_to_buyer = fields.Text(
        string="Info to Buyer",
        copy=False,
        help='Information to buyer',
    )
    info_to_production = fields.Text(
        string="Info to Production",
        help="Information provided to the production team."
    )
    type_product = fields.Selection(
        selection=[
            ('int', 'INT'),
            ('ext', 'EXT'),
            ('hdl', 'HDL'),
        ],
        string="Type",
        store=True,
        help="Type Proction",
        default='int'
    )

    supp_order = fields.Many2one(
        'res.partner',
        string="Supp",
        store=True,
    )

    external_id = fields.Many2one(
        'sale.id.external',
        string="External ID",
        help="Pilih ID External untuk produk ini",
    )

    sec_price = fields.Float(
        string="OM Price",
        help="OM Price"
    )

    total_sec_price = fields.Float(
        string='Total Cust Price', 
        compute='_compute_total_sec_price',
        store=True
    )

    @api.depends('sec_price', 'original_uom_qty')
    def _compute_total_sec_price(self):
        for record in self:
            record.total_sec_price = record.sec_price * record.original_uom_qty

    finish = fields.Char(string='Finish')

    due_date_item_update = fields.Date(string='Due Date Item Update')

    color_attribute_size = fields.Char(string='Color / Attribute / Size')

    analytic_names = fields.Char(compute='_compute_analytic_names', string='Analytic Names')

    def _compute_analytic_names(self):
        for line in self:
            if line.analytic_distribution:
                ids = [int(i) for i in line.analytic_distribution.keys()]
                names = self.env['account.analytic.account'].browse(ids).mapped('name')
                line.analytic_names = ', '.join(names)
            else:
                line.analytic_names = ''


