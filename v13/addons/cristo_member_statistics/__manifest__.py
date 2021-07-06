# -*- coding: utf-8 -*-
{
    'name': 'Cristo Member Statistics',
    'version': '2.0',
    'category': '',
    'sequence': 2,
    'summary': 'Parish Management Software',
    'description': """Parish Management Software""",
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'cristo',
               ],
    'data': [
                'security/ir.model.access.csv',
                'report/member_statistics_view.xml',
                'views/member_views.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
