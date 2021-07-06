{
    'name': 'Cristo Circular',
    'version': '2.0',
    'category': '',
    'sequence': 4,
    'summary': 'Circular',
    'description': """Cristo Circular""",
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'cristo_dashboard', 'cristo', 'cristo_calendar_meeting'
               ],
    'data': [
#             security
             'security/circular_security.xml',
             'security/ir.model.access.csv',
             
#             data
             'data/circular_mail_template.xml',
#              wizard
            'wizard/wizard_circular_mail.xml',
#             views
             'views/circular_views.xml',
             'views/res_religious_views.xml',
             'views/report/circular_template.xml',
             'views/report/circular_report.xml',
             'views/menus.xml',
             'views/dashboard_assets.xml',
            ],
    'qweb': ['static/src/xml/dashboard.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
