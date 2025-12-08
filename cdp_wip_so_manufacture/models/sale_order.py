from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    cdp_product_wip_id = fields.Many2one(
        "product.product", string="WIP Product", readonly=True, copy=False
    )
    