{
    'name': 'Cristo Asset',
    'version': '2.0',
    'category': '',
    'sequence': 7,
    'summary': 'Asset',
    'description': """Cristo Asset""",
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
                'cristo',
               ],
    'data': [
#             security
            'security/cristo_asset_security.xml',
            'security/ir.model.access.csv',
       
#             views
            'views/res_asset_config.xml',
            'views/res_asset_view.xml',
            'views/cristo_asset_menus.xml',
            ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
