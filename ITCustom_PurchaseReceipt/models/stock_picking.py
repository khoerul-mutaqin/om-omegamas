from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'



    def action_add_products(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Products from Purchase Order',
            'res_model': 'add.products.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
            }
        }
