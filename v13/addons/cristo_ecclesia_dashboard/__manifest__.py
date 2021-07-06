# -*- coding: utf-8 -*-
{
    'name': 'Cristo Ecclesia Dashboard',
    'version': '2.0',
    'category': 'Dashboard',
    'sequence': 3,
    'summary': 'Parish Management Software',
    'description': """ """,
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'base',
                'web',
                'cristo_dashboard',
               ],
    'data': [
            'views/diocese_dashboard_views.xml',
            'views/ecclesia_views.xml',
            ],
    'qweb': ["static/src/xml/*.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}
