{
    'name': 'Cristo CRI',
    'version': '2.0',
    'category': '',
    'sequence': 4,
    'summary': 'Cristo CRI',
    'description': """Cristo CRI""",
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'cristo_dashboard', 'cristo'
               ],
    'data': [
#             security
             'security/ir.model.access.csv',
             
#             views
             'views/res_religious_views.xml',
             'views/report/report_rel_province_profile_inherit.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
