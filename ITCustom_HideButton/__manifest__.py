# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'ITCustom Hide Button',
    'version': '18.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Hide specific buttons for users in Odoo forms',
    'description': 'Allow administrators to hide specific buttons (like Confirm Order) for certain users in purchase orders and other forms.',
    'author': 'ITCustom',
    'company': 'ITCustom',
    'maintainer': 'ITCustom',
    'website': "https://www.itcustom.com",
    'depends': ['base', 'purchase', 'om_purchase_manual_delivery', 'sale', 'sale_blanket_order', 'account'],
    'data': [
        'security/security.xml',
        'data/itcustom_button_data.xml',
        'views/itcustom_button_views.xml',
        'views/res_users_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/sale_blanket_order_views.xml',
        'views/purchase_request_views.xml',
        'views/button_discovery_views.xml',
        'views/account_move_views.xml',
    ],
    'license': 'LGPL-3',
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
