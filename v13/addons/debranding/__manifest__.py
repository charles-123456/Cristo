# -*- coding: utf-8 -*-
{
    'name': "Cristo Debranding",
    'version': "13.0.1.0.0",
    'summary': """Debrand""",
    'description': """Debranding""",
    'author': "Boscosoft Technologies",
    'company': "Boscosoft Technologies",
    'maintainer': "Boscosoft Technologies",
    'website': "",
    'category': 'Tools',
    'depends': ['base','mail','mail_bot'],
    'data': [
        'views/views.xml',
        'views/res_users_view.xml'
    ],
    'qweb': ["static/src/xml/*.xml"],
    'images': [],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
