{
    'name': 'Pengobatan',
    'summary': 'App to manage and book meeting rooms.',
    'description': '''
        Manage meeting rooms, book schedules, and prevent double bookings.
    ''',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'license': 'LGPL-3', 
    'author': 'Taufiqur Rahman',
    'website': 'http://www.omegamas.com',
    'depends': [
        'base', 'hr',
    ],
    'data': [
        
        'security/ir.model.access.csv',
        'views/alokasi_views.xml',
        'views/klaim_views.xml',
        'views/actions.xml',
        'views/menus.xml',
        'views/export_klaim_wizard_view.xml',
    ],
    
    'installable': True,
    'application': True,

}
