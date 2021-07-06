# -*- coding: utf-8 -*-
{
    'name': 'Cristo Assignment',
    'version': '2.0',
    'category': '',
    'sequence': 5,
    'summary': 'Parish Management Software',
    'description': """ """,
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'cristo','export_xlsx','report_xlsx','cristo_dashboard',
               ],
    'data': [
                'security/cristo_assignment_security.xml',
                'security/ir.model.access.csv',
                'data/request_server_action.xml',
#                 'views/res_configuration_views.xml',
                'views/res_member_views.xml',
                'views/assignment_views.xml',
                'wizard/assignment_upload.xml',
                'views/report_xlsx.xml',
                'views/dashboard_assets.xml',
                'views/report/transfer_report.xml',
                'views/report/transfer_details.xml',
                'views/menus.xml',
            ],
    'qweb': ['static/src/xml/dashboard.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}