{
    'name': 'CristO Directory',
    'version': '2.0',
    'category': '',
    'sequence': 4,
    'summary': 'Directory',
    'description': """CristO Directory""",
    'author': 'Boscosoft Technologies Pvt Ltd',
    'website': 'https://www.boscosofttech.com',
    'depends': [
            'cristo','web','mail','base','report_xlsx',
    ],
    'data': [
        'security/cristo_directory_security.xml',
        'security/ir.model.access.csv',
        'views/res_directory_views.xml',
        'views/res_religious_views.xml',
        'views/cristo_directory_assets.xml',
        'views/report/directory_report_xlsx.xml',
    ],
    'qweb': [
        'static/src/xml/cristo_directory.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
