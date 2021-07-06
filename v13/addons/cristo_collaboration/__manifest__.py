{
    'name': 'Cristo Collaboration',
    'version': '2.0',
    'category': '',
    'sequence': 4,
    'summary': 'Collaboration',
    'description': """Cristo Collaboration""",
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'cristo_dashboard','cristo',
               ],
    'data': [
             'security/ir.model.access.csv',
             
             'views/collaboration_views.xml',
             'views/res_religious_views.xml',
             'views/res_ecclesia_views.xml',
            ],
    'qweb': [
        
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
