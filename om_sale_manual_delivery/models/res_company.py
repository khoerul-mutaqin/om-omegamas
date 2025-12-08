# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    sale_manual_delivery = fields.Boolean(
        string="Sale manual delivery?", required=False
    )
