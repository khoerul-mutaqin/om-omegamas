{
    'name': 'Document Duplicate Name Handler',
    'version': '1.0',
    'summary': 'Prevent duplicate file names in Odoo Documents by adding suffix',
    'description': """
        This module prevents duplicate file names in Odoo Documents by automatically renaming files
        with a suffix (e.g., 1(2).jpg) when a file with the same name is uploaded to the same folder.
    """,
    'category': 'Document Management',
    'author': 'Your Name/Your Company',
    'depends': ['documents'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
