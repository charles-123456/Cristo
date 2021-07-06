# -*- coding: utf-8 -*-
{
    'name': "HelpDesk",
    'version': "1.0",
    'category': "",
    'summary': "A helpdesk / support ticket system",
    'description': """  """,
    'author': 'Boscosoft Technologies Pvt Ltd',
    'license':'LGPL-3',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'base', 'mail', 'portal'
               ],
    'data': [
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
        
        'data/helpdesk_data.xml',
        
        'views/helpdesk_tickets.xml',
        'views/helpdesk_team_views.xml',
        'views/helpdesk_stage_views.xml',
        'views/res_config_views.xml',
        'views/helpdesk_templates.xml',
        'views/menus.xml',

    ],
    'demo': [
        'demo/helpdesk_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
