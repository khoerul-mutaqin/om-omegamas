from odoo import fields, models, api


class SuppOrder(models.Model):
    _name = 'supp.order'
    _description = 'Supplier Order'

    name = fields.Char(
        string="Supplier",
        required=True,
    )
