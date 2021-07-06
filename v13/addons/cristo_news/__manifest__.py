# -*- coding: utf-8 -*-
{
    'name': 'Cristo News',
    'version': '2.0',
    'category': 'News',
    'sequence': 3,
    'summary': 'Parish Management Software',
    'description': """ """,
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'cristo',
                'cristo_dashboard',
                'cristo_ecclesia_dashboard',
               ],
    'data': [
            'security/ir.model.access.csv',
            'security/news_security.xml',
            
            'views/res_news_views.xml',
            'views/res_religious_views.xml',
            'views/res_ecclesia_views.xml',
            'views/dashboard_views.xml',
            ],
    'qweb': ["static/src/xml/*.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}
