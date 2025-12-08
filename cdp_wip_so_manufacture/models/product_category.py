from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    cdp_for_product_wip = fields.Boolean(
        string="For WIP Product",
        default=False,
        help="If checked, this category is used for WIP products.",
    )
