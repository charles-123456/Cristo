{
    'name': 'Cristo User Management',
    'version': '2.0',
    'category': '',
    'sequence': 4,
    'summary': 'User Management',
    'description': """Cristo Circular""",
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'base','cristo','cristo_dashboard'
               ],
    'data': [
#             security
            'security/users_security.xml',
            'security/ir.model.access.csv',
#             data
            'data/cron_file.xml',
            'data/mail_template_data.xml',
#             views
            'views/webclient_templates.xml',
            'wizard/wizard_change_password.xml',
            'views/user_license.xml',
            'views/users_views.xml',
            'views/menus.xml',
            ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
