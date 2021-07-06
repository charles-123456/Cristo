# -*- coding: utf-8 -*-
{
    'name': 'Cristo Chronicle',
    'version': '2.0',
    'category': '',
    'sequence': 2,
    'summary': 'Parish Management Software',
    'description': """ """,
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'mail','cristo_dashboard','cristo','cristo_calendar_meeting','muk_dms'
               ],
    'data': [
                'security/cristo_chronicle_security.xml',
                'security/ir.model.access.csv',
                
                'wizard/report/wizard_chronicle.xml',
                
                'views/chronicle_views.xml',
                'views/res_religious_views.xml',
                'views/chronicle/chronicle.xml',
                'views/chronicle/chronicle_template.xml',
                'views/chronicle/chronicle_report.xml',
                'views/dashboard_views.xml',
                'views/file_views.xml',
                'views/menus.xml',
                
            ],
    'qweb': ["static/src/xml/*.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}
