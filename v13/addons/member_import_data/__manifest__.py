# -*- coding: utf-8 -*-
{
    'name': 'Cristo Member Import Data',
    'version': '2.0',
    'category': '',
    'sequence': 2,
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'base','cristo',
               ],
    'data': [
        'views/reports/template_reports.xml',
        'wizard/update_profession.xml',
        'wizard/update_formation.xml',
        'wizard/update_holyorder.xml',
        'wizard/update_education.xml',
        'wizard/publication/update_publication.xml',
        'wizard/member_health/update_member_health.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
