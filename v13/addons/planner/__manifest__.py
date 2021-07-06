# -*- coding: utf-8 -*-
{
    'name': 'Project Planner',
    'version': '1.0',
    'category': 'Planner',
    'sequence': 4,
    'summary': 'Project Planner',
    'description': """Project Planner""",
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': ['base','web'],
    'external_dependencies': {
        'python' : ['python-docx','python-docx-whtsky'],
        },
    'data': [
            'security/planner_security.xml',
            'security/ir.model.access.csv',
            
            'wizard/wizard_activity.xml',
            'wizard/wizard_expenditure.xml',
            
            'views/report/activity_template.xml',
            'views/report/expenditure_template.xml',
            'views/report/planner_reports.xml',
            'views/project_planner_views.xml',
            'views/planner_config_views.xml',
            'views/webclient_template.xml',
            'views/menus.xml',
            ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
