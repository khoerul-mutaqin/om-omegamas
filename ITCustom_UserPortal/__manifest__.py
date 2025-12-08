{
    'name': 'User Portal Enhancements',
    'version': '1.0',
    'depends': ['project', 'portal', 'web'],
    'category': 'Tools',
    'summary': 'Beautify User Portal Projects Page',
    'description': 'Module to enhance the UI of the /my/projects page',
    'data': [
        'views/portal_my_projects_inherit.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ITCustom_UserPortal/static/src/css/user_portal.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
