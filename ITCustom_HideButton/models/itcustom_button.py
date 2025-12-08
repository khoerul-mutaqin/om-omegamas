# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from odoo import fields, models, api
from odoo.exceptions import UserError

class ItCustomButton(models.Model):
    """
    Model to represent buttons that can be hidden for certain users.
    """
    _name = 'itcustom.button'
    _description = 'Button to Hide'

    name = fields.Char(string='Button Name', required=True, help='Unique identifier for the button')
    model = fields.Char(string='Model', required=True, help='Model where the button is located (e.g., purchase.order)')
    button_name = fields.Char(string='Button Name Attribute', required=True, help='The name attribute of the button in XML')
    button_string = fields.Char(string='Button Label', help='The display text of the button')
    description = fields.Text(string='Description', help='Description of the button')
    
    restrict_user_ids = fields.Many2many(
        'res.users', 
        string="Restricted Users",
        help='Users restricted from seeing this button.',
        # Pastikan nama tabel relasional sama
        relation='itcustom_button_res_users_rel',
        column1='itcustom_button_id',
        column2='res_users_id'
    )

    @api.model
    def create(self, vals):
        """
        Create method to handle initial synchronization
        """
        record = super(ItCustomButton, self).create(vals)
        # Sinkronisasi setelah create jika ada user restrictions
        if 'restrict_user_ids' in vals:
            record._sync_restrict_users()
        return record

    def write(self, vals):
        """
        Write method to sync restrict_user_ids with users' hide_button_ids.
        """
        res = super(ItCustomButton, self).write(vals)
        if 'restrict_user_ids' in vals and not self.env.context.get('syncing_hide_buttons'):
            self._sync_restrict_users()
        return res

    def _sync_restrict_users(self):
        """
        Synchronize restrict_user_ids with the relational table
        """
        for record in self:
            # Dapatkan semua user yang terkait dengan button ini
            related_users = record.restrict_user_ids
            
            # Update hide_button_ids di user side
            for user in related_users:
                user.with_context(syncing_hide_buttons=True).write({
                    'hide_button_ids': [(4, record.id)]
                })
            
            # Handle removed users
            previous_users = self.env['res.users'].search([
                ('hide_button_ids', 'in', [record.id])
            ])
            removed_users = previous_users - related_users
            for user in removed_users:
                user.with_context(syncing_hide_buttons=True).write({
                    'hide_button_ids': [(3, record.id)]
                })

    view_id = fields.Many2one('ir.ui.view', string="View", help="The view where the button is defined")

    _sql_constraints = [
        ('unique_button', 'unique(model, button_name, view_id)', 'Button must be unique per model, name and view'),
    ]

    @api.model
    def _discover_all_buttons(self):
        """
        Discover all buttons from all installed views.
        """
        # Get all installed views
        views = self.env['ir.ui.view'].search([('type', '=', 'form')])

        discovered_buttons = []
        for view in views:
            buttons = self._extract_buttons_from_view(view)
            discovered_buttons.extend(buttons)

        # Update or create button records
        for button_data in discovered_buttons:
            existing = self.search([
                ('model', '=', button_data['model']),
                ('button_name', '=', button_data['button_name']),
                ('view_id', '=', button_data['view_id']),
            ], limit=1)

            if existing:
                existing.write({
                    'name': button_data['name'],
                    'button_string': button_data['button_string'],
                    'description': button_data.get('description', ''),
                    'active': True,
                })
            else:
                self.create(button_data)

        # Deactivate buttons that are no longer found
        all_buttons = self.search([])
        found_combinations = [(b['model'], b['button_name'], b['view_id']) for b in discovered_buttons]
        for button in all_buttons:
            if (button.model, button.button_name, button.view_id.id) not in found_combinations:
                button.active = False

    def _extract_buttons_from_view(self, view):
        """
        Extract button information from a view's XML architecture.
        """
        buttons = []

        try:
            # Parse the XML architecture
            root = ET.fromstring(view.arch)

            # Find all button elements
            for button in root.iter('button'):
                button_data = self._parse_button_element(button, view)
                if button_data:
                    buttons.append(button_data)

        except Exception as e:
            # Log error but continue with other views
            self.env['ir.logging'].create({
                'name': 'Button Discovery Error',
                'type': 'server',
                'level': 'WARNING',
                'message': f'Error parsing view {view.name} ({view.id}): {str(e)}',
                'path': 'itcustom.button.discovery',
                'line': '0',
                'func': '_extract_buttons_from_view',
            })

        return buttons

    def _parse_button_element(self, button_element, view):
        """
        Parse a button XML element and extract relevant information.
        """
        button_name = button_element.get('name')
        button_string = button_element.get('string')
        button_type = button_element.get('type', 'object')

        # Skip buttons without names or certain types
        if not button_name or button_type not in ['object', 'action']:
            return None

        # Determine the model (use view.model if available)
        model = view.model

        # Generate a descriptive name
        name = button_string or button_name.replace('_', ' ').title()

        # Create description
        description = f"Button '{name}' in {model} form"

        return {
            'name': name,
            'model': model,
            'button_name': button_name,
            'button_string': button_string,
            'view_id': view.id,
            'description': description,
            'active': True,
        }
