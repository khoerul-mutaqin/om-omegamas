from odoo import api, fields, models


class MrpProductionBackorder(models.TransientModel):
    _inherit = 'mrp.production.backorder'
