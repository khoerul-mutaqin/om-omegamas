from odoo import api, fields, models


class ButtonDiscovery(models.TransientModel):
    """
    Wizard to discover and update available buttons from all installed modules.
    """
    _name = 'itcustom.button.discovery'
    _description = 'Button Discovery Wizard'

    def action_discover_buttons(self):
        """
        Discover all buttons from installed views and update the button registry.
        """
        self.env['itcustom.button']._discover_all_buttons()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }



