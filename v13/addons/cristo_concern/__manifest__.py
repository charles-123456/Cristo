{
    'name': 'Cristo Concern',
    'version': '2.0',
    'category': '',
    'sequence': 4,
    'summary': 'Concern',
    'description': """Cristo Concern""",
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'cristo_dashboard','cristo',
               ],
    'data': [
             'security/cristo_concern_security.xml',
             'security/ir.model.access.csv',
             
             'views/concern_views.xml',
             'views/configuration_views.xml',
             'views/report/concern.xml',
             'views/report/concern_template.xml',
             'views/menus.xml',
             'views/dashboard_assets.xml',
            ],
    'qweb': [
        'static/src/xml/dashboard.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
